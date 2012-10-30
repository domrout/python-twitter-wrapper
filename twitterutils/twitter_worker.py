import twitterwrapper, sys, string, re, anyjson, argparse, time, urllib2, os

from Queue import Queue, Empty
from threading import Thread, Event
from itertools import izip


class TwitterDispatcher(Thread):
  """Generic class for that manages a number of twitter collection tasks on several public
    keys"""
  def __init__(self, tasks, id_file="__tasks.id", token_store=None):
    """Parameter tasks should be an iterable producing a list of tasks to complete"""
    Thread.__init__(self)

    self.token_store = twitterwrapper.access_tokens.AccessTokenStore()
    self.token_store.load()

    # Ensure all connections are initialized
    for auth in self.token_store.tokens.itervalues():
      auth["connection"] = twitterwrapper.Connection(**auth)

    self.tweetThreadQueue = Queue(len(self.token_store.tokens)) # Only queue as many tasks are there are accounts

    self.completionManager = CompletionManager(id_file)   
    self.completionManager.load()
    self.workers = list()
    self.tasks = tasks
    
    self.stopped = Event()

  def run(self):
    """Reads the tasks and starts working."""        
    self.start_workers()
    
    for task in self.tasks:
      if self.stopped.is_set():
          break

      if not self.completionManager.is_done(task):
        self.tweetThreadQueue.put(task)
    
    self.tweetThreadQueue.join()
    self.completionManager.stop()

    
  def start_workers(self):
      """Creates worker threads for each authentication available."""
      for username, auth in self.token_store.tokens.iteritems():
          flw = TwitterWorker(twitterwrapper.Api(auth["connection"]), 
            username, 
            self.completionManager,
            self.tweetThreadQueue)

          flw.daemon = True
          self.workers.append(flw)
          flw.start()
                  
      self.completionManager.start()
      
  def stop(self):
      self.stopped.set()
      
      # Try to empty the queue
      try:
          while self.tweetThreadQueue.get_nowait():
             self.tweetThreadQueue.task_done()
      except Empty:
          pass
          
      self.completionManager.stop()
      # Stop all worker threads
      for worker in self.workers:
          worker.stop()
                       
                
class TwitterWorker(Thread):
    """A worker thread to hold a connection to the Twitter API and execute tasks."""
        
    def __init__(self, connection, screen_name, completionManager, queue):
        Thread.__init__(self)
          
        self.api = connection
        self.screen_name = screen_name
        
        #self.api.VerifyCredentials().screen_name
        self.completionManager = completionManager
        self.queue = queue
        self.stopped = Event()

    def run(self):
        api = self.api
    
        while True:
            task = self.queue.get()
            try:
                # Check to see if we've hit the rate limit.
                limit_status = api.account.rate_limit_status()

                if (limit_status.remaining_hits < 2):
                  time_to_wait = limit_status.reset_time_in_seconds - time.time()

                  print "Rate limit hit on a thread, waiting  %i minutes..." % int(time_to_wait/60)
                  self.stopped.wait(time_to_wait + 10)
        
                task.run(self.api, self.screen_name)

                self.completionManager.done(task)
                self.queue.task_done()

            except Exception as e:
                print "Error on thread for user %s" % self.screen_name
                print e

                # Skip tasks with "Not authorized" errors and never try again
                if e.message == "Not authorized":
                  self.completionManager.done(task)
                  print "------- Will not try tasks which gave this type of error ever again"
        
    def stop(self):
        self.stopped.set()
        
class CompletionManager(Thread):
    """Tracks the completion of task ids."""
    def __init__(self, output):
        Thread.__init__(self)
        self.queue = Queue()
        self.output = output
        self.stopped = Event()

        self.complete_ids = set()
        

    def load(self):
      if os.path.exists(self.output):
        with open(self.output) as f:
           for l in f:
              id = l.strip()
              self.complete_ids.add(id)

    def run(self):
        with open(self.output, 'a') as f:
            while not self.stopped.is_set():
                try:
                    task = self.queue.get(timeout=10)
                    print >> f, task.get_id()

                    self.complete_ids.add(task.get_id())
                except Empty:
                    pass # Nothing to do - go around again.
                    
    def done(self, task):
        self.queue.put(task)
    
    def is_done(self, task):
        return task.get_id() in self.complete_ids

    def stop(self):
        """Stops the process from running. May take up to 10 seconds."""
        self.stopped.set()
        
class TwitterTask:
  """A task which relies on an instance of the Twitter API."""
  def __init__(self):
    self.limit_status = None

  def run(self, api, screen_name):
    """Called when it is time to run this task. API is an instance of the Twitter
      API.

      If you need to write some results to a file, from this task, call writer.write(self)"""
    self.limit_status = api.account.rate_limit_status()

  def get_id(self):
    return 1
