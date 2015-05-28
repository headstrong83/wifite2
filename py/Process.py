#!/usr/bin/python

from subprocess import Popen, call, PIPE

class Process(object):
    ''' Represents a running/ran process '''

    @staticmethod
    def devnull():
        ''' Helper method for opening devnull '''
        return open('/dev/null', 'w')

    @staticmethod
    def call(command):
        '''
            Calls a command (either string or list of args).
            Returns tuple:
                (stdout, stderr)
        '''
        if type(command) != str or ' ' in command:
            shell = True
        else:
            shell = False
        pid = Popen(command, stdout=PIPE, stderr=PIPE, shell=shell)
        pid.wait()
        return pid.communicate()

    @staticmethod
    def exists(program):
        ''' Checks if program is installed on this system '''
        p = Process(['which', program])
        if p.stdout().strip() == '' and p.stderr().strip() == '':
            return False
        return True


    def __init__(self, command, devnull=False):
        ''' Starts executing command '''
        if type(command) == str:
            # Commands have to be a list
            command = command.split(' ')
        self.out = None
        self.err = None
        if devnull:
            sout = Process.devnull()
            serr = Process.devnull()
        else:
            sout = PIPE
            serr = PIPE
        self.pid = Popen(command, stdout=sout, stderr=serr)

    def stdout(self):
        ''' Waits for process to finish, returns stdout output '''
        self.get_output()
        return self.out

    def stderr(self):
        ''' Waits for process to finish, returns stderr output '''
        self.get_output()
        return self.err

    def get_output(self):
        ''' Waits for process to finish, returns stdout & stderr '''
        if self.pid.poll() == None:
            self.pid.wait()
        if self.out == None:
            (self.out, self.err) = self.pid.communicate()

    def poll(self):
        ''' Returns exit code if process is dead, otherwise "None" '''
        return self.pid.poll()

    def interrupt(self):
        '''
            Send interrupt to current process.
            If process fails to exit within 1 second, terminates it.
        '''
        from signal import SIGINT, SIGTERM
        from os import kill
        from time import sleep
        try:
            pid = self.pid.pid
            kill(pid, SIGINT)

            wait_time = 0 # Time since Interrupt was sent
            while self.pid.poll() == None:
                # Process is still running
                wait_time += 0.1
                sleep(0.1)
                if wait_time > 1:
                    # We waited over 1 second for process to die
                    # Terminate it and move on
                    kill(pid, SIGTERM)
                    self.pid.terminate()
                    break
                    
        except OSError, e:
            if 'No such process' in e.__str__():
                return
            raise e  # process cannot be killed

if __name__ == '__main__':
    p = Process('ls')
    print p.stdout(), p.stderr()
    p.interrupt()

    # Calling as list of arguments
    (out,err) = Process.call(['ls', '-lah'])
    print out,err

    print '\n---------------------\n'

    # Calling as string
    (out,err) = Process.call('ls -l | head -2')
    print out,err

    print '"reaver" exists:', Process.exists('reaver')
