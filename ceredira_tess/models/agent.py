import logging
import os
import subprocess

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

from ceredira_tess.database import Base, db_session
from ceredira_tess.models import relationships


class Agent(Base):
    __tablename__ = 'agent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(128), nullable=False, unique=True)
    description = Column(Text)
    lock_cause = Column(Text)

    lock_user_id = Column(Integer, ForeignKey('user.id'))
    lock_user = relationship('User', backref=backref('agents', lazy='dynamic'))

    operationsystemtype_id = Column(Integer, ForeignKey('operationsystemtype.id'),
                                    nullable=False)
    operationsystemtype = relationship('OperationSystemType', backref=backref('agents', lazy='dynamic'))
    scripts = relationship('Script', secondary=relationships.agents_scripts)
    roles = relationship("Role", secondary=relationships.roles_agents, back_populates='agents')

    def __repr__(self):
        return f'{self.hostname}'

    def __init__(self, hostname, operationsystemtype):
        self.hostname = hostname
        self.operationsystemtype = operationsystemtype

    def add_role(self, role):
        self.roles.append(role)

    def lock(self, lock_user, lock_cause):
        list_of_agents = [agent for x in lock_user.roles for agent in x.agents]
        if self in list_of_agents:
            if self.lock_user is None:
                self.lock_user = lock_user
                self.lock_cause = lock_cause
                db_session.commit()
                return True, f'Agent {self.hostname} locked'
            elif self.lock_user == lock_user:
                return False, f'Agent {self.hostname} already locked by you, but with a cause: {self.lock_cause}'
            else:
                return False, f'Agent {self.hostname} locked by another user'
        else:
            return False, f'User cannot access to agent {self.hostname}'

    def unlock(self, lock_user, lock_cause):
        list_of_agents = [agent for x in lock_user.roles for agent in x.agents]
        if self in list_of_agents:
            if self.lock_user is None:
                return True, f'Agent {self.hostname} already unlocked'
            if self.lock_user == lock_user:
                if self.lock_cause == lock_cause:
                    self.lock_user = None
                    self.lock_cause = None
                    db_session.commit()
                    return True, f'Agent {self.hostname} unlocked'
                else:
                    return False, f'Cannot unlock agent {self.hostname}, locked with another cause: {self.lock_cause}'
            return False, f'Cannot unlock agent {self.hostname}, locked with another user'
        else:
            return False, f'User cannot access to agent {self.hostname}'

    def execute_script_with_timeout(self, root_path, script, psexec_options=None, args_list=None,
                                    encoding='utf-8',
                                    timeout=60):
        logger = logging.getLogger("CerediraTess.Agent.execute_script_with_timeout")
        logger.debug(
            f'Execute run_with_timeout with args: {root_path}, {script}, {args_list}, {encoding}, {timeout}')
        try:
            if self.hostname == 'CerediraTess':
                return self.execute_script_locally(root_path, script, args_list, encoding, timeout)
            else:
                return self.execute_script_remote(root_path, script, psexec_options, args_list, encoding,
                                                  timeout)
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
            return f"Error while create process: {e}"

    def execute_script_locally(self, root_path, script, args_list=None, encoding='utf-8', timeout=60):
        if args_list is None:
            args_list = []
        logger = logging.getLogger("CerediraTess.Agent.execute_script_locally")

        proc = [os.path.join(root_path, 'scripts', script)]
        proc.extend(args_list)

        try:
            output = subprocess.check_output(proc, encoding=encoding, timeout=timeout, stderr=subprocess.STDOUT,
                                             errors='replace')
        except subprocess.CalledProcessError as grepexc:
            output = f'Finish with error: {grepexc.returncode}\n\n{grepexc.output}'
        except Exception as ex:
            output = f'Exception while execution: {ex}'

        logger.debug(f'Script execution result:\n{output}')

        return output

    def execute_script_remote(self, root_path, script, psexec_options=None, args_list=None, encoding='utf-8',
                              timeout=60):
        logger = logging.getLogger("CerediraTess.Agent.execute_script_remote")

        if args_list is None:
            args_list = []
        if psexec_options is None:
            psexec_options = {}

        if self.operationsystemtype.osname == 'Windows':
            proc = [os.path.join(root_path, 'resources\\psexec.exe')]
            if 'username' in psexec_options and psexec_options['username'] is not None:
                proc.extend(['-u', psexec_options['username']])
            if 'password' in psexec_options and psexec_options['password'] is not None:
                proc.extend(['-p', psexec_options['password']])

            proc.extend([f'\\\\{self.hostname}', '-accepteula', '-nobanner', '-f'])
            proc.extend(['-c', os.path.join(root_path, 'scripts', script)])
            proc.extend(args_list)
        else:
            proc = [os.path.join(root_path, 'resources\\plink.exe')]
            if 'username' in psexec_options and psexec_options['username'] is not None:
                proc.extend(['-l', psexec_options['username']])
            if 'password' in psexec_options and psexec_options['password'] is not None:
                proc.extend(['-pw', psexec_options['password']])
            if 'port' in psexec_options and psexec_options['port'] is not None:
                proc.extend(['-P', psexec_options['port']])

            proc.extend([self.hostname, '-ssh', '-batch'])
            proc.extend(args_list)
            proc.extend(['-m', os.path.join(root_path, 'scripts', script)])

        exec_command = ''
        for i in proc:
            exec_command += f'{i} '
        logger.info(exec_command)

        try:
            output = subprocess.check_output(proc, encoding=encoding, timeout=timeout, stderr=subprocess.STDOUT,
                                             errors='replace')
        except subprocess.CalledProcessError as grepexc:
            output = f'Finish with error: {grepexc.returncode}\n\n{grepexc.output}'
        except Exception as ex:
            output = f'Exception while execution: {ex}'

        logger.debug(f'Script execution result:\n{output}')

        return output
