import threading
import traceback


from .preview_utils import try_delete_temp_files

_max_threads = 2
_thread_num_lock = threading.Lock()
_thread_num = 0
_jobs_lock = threading.Lock()
_jobs = {}
_working_sets = {}
_working_sets_lock = threading.Lock()

# folder path to delete for each job
_temp_folder_paths = {}
# execute job functions for each job
_thread_functions = {}


def set_max_threads(max_threads):
    global _max_threads
    if max_threads > 0 and max_threads != _max_threads:
        _max_threads = max_threads


def has_function(_name):
    return _name in _thread_functions


def register_function(name, func):
    _thread_functions[name] = func


def register_temp_folder(name, temp_path):
    _temp_folder_paths[name] = temp_path


def _cancel_jobs(name, is_target_job):
    try:
        lock, job_list = _jobs[name]
    except KeyError:
        return
    with lock:
        delete_jobs = [job for jid, job in job_list if is_target_job(job)]
        for job in delete_jobs:
            try:
                job_list.remove(job)
            except ValueError:
                pass


def cancel_jobs(name, is_target_job):
    with _jobs_lock:
        _cancel_jobs(name, is_target_job)


def _extend_jobs(name, extend_job_list):
    if name not in _jobs:
        _jobs[name] = (threading.Lock(), [])
    lock, job_list = _jobs[name]
    with lock:
        job_list.extend(extend_job_list)


def extend_jobs(name, extend_job_list):
    with _jobs_lock:
        _extend_jobs(name, extend_job_list)


def _append_job(name, jid, job):
    if name not in _jobs:
        _jobs[name] = (threading.Lock(), [])
    lock, job_list = _jobs[name]
    with lock:
        job_list.append((jid, job))


def append_job(name, jid, job):
    with _jobs_lock:
        _append_job(name, jid, job)


def _start_threads(name, thread_id):
    try:
        func = _thread_functions[name]
    except KeyError:
        print("Thread function missing for '{0}'".format(name))
        return
    try:
        lock, job_list = _jobs[name]
    except KeyError:
        return

    with _working_sets_lock:
        if name not in _working_sets:
            _working_sets[name] = set()
        working_set = _working_sets[name]

    while True:
        try:
            with lock:
                head = job_list.pop()
                jid, job = head
                if jid is not None and jid in working_set:
                    job_list.append(head)
                    for i in range(len(job_list)):
                        jid, job = job_list[i]
                        if jid not in working_set:
                            del job_list[i]
                            break
                    else:
                        raise StopIteration()

            with lock:
                working_set.add(jid)
            func(job)
            with lock:
                working_set.remove(jid)
        except IndexError:
            break
        except StopIteration:
            break
        except Exception:
            traceback.print_exc()
            break
        if thread_id >= _max_threads:
            break


def start_threads(name, thread_id):
    _start_threads(name, thread_id)

    visited = set([name])

    while True:
        new_name = None
        for key, (lock, joblist) in _jobs.items():
            with lock:
                if joblist:
                    new_name = key
                    break

        if not new_name or new_name in visited:
            break

        if new_name and new_name != name:
            _start_threads(new_name, thread_id)

    global _thread_num
    with _thread_num_lock:
        _thread_num -= 1
        remaining_threads = _thread_num

    # if all threads have been terminated we can check to delete
    # the temporary files beyond the size limit
    if remaining_threads == 0:
        for v in visited:
            try:
                temp_path = _temp_folder_paths[v]
            except KeyError:
                continue

            threading.Thread(
                target=lambda: try_delete_temp_files(name, temp_path))


def run_jobs(name):
    global _thread_num, _max_threads
    thread_id = -1

    with _jobs_lock:
        try:
            lock, job_list = _jobs[name]
        except KeyError:
            return
    # we may not need locks for this
        with lock:
            rem_len = len(job_list)
        with _thread_num_lock:
            before_num = _thread_num
            after_num = min(_max_threads, rem_len)
            start_threads_count = after_num - before_num
            if start_threads_count > 0:
                _thread_num += start_threads_count
        for thread_id in range(before_num, after_num):
            threading.Thread(target=start_threads,
                             args=(name, thread_id,)).start()
