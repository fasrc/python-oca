# -*- coding: UTF-8 -*-
from pool import Pool, PoolElement, ET


class VirtualMachine(PoolElement):
    METHODS = {
        'info'     : 'vm.info',
        'allocate' : 'vm.allocate',
        'action'   : 'vm.action',
        'migrate'  : 'vm.migrate',
        'deploy'   : 'vm.deploy',
        'savedisk' : 'vm.savedisk',
        'delete'   : 'vm.delete',
    }

    VM_STATE = ['INIT', 'PENDING', 'HOLD', 'ACTIVE', 'STOPPED', 'SUSPENDED', 'DONE', 'FAILED']

    SHORT_VM_STATES = {
        'INIT'      : 'init',
        'PENDING'   : 'pend',
        'HOLD'      : 'hold',
        'ACTIVE'    : 'actv',
        'STOPPED'   : 'stop',
        'SUSPENDED' : 'susp',
        'DONE'      : 'done',
        'FAILED'    : 'fail'
    }

    LCM_STATE = ['LCM_INIT', 'PROLOG', 'BOOT', 'RUNNING', 'MIGRATE', 'SAVE_STOP', 'SAVE_SUSPEND',
                 'SAVE_MIGRATE', 'PROLOG_MIGRATE', 'PROLOG_RESUME', 'EPILOG_STOP', 'EPILOG',
                 'SHUTDOWN', 'CANCEL', 'FAILURE', 'DELETE', 'UNKNOWN',]

    SHORT_LCM_STATES = {
        'LCM_INIT'      : 'init',
        'PROLOG'        : 'prol',
        'BOOT'          : 'boot',
        'RUNNING'       : 'runn',
        'MIGRATE'       : 'migr',
        'SAVE_STOP'     : 'save',
        'SAVE_SUSPEND'  : 'save',
        'SAVE_MIGRATE'  : 'save',
        'PROLOG_MIGRATE': 'migr',
        'PROLOG_RESUME' : 'prol',
        'EPILOG_STOP'   : 'epil',
        'EPILOG'        : 'epil',
        'SHUTDOWN'      : 'shut',
        'CANCEL'        : 'shut',
        'FAILURE'       : 'fail',
        'DELETE'        : 'dele',
        'UNKNOWN'       : 'unkn',
    }

    MIGRATE_REASON = ['NONE', 'ERROR', 'STOP_RESUME', 'USER', 'CANCEL']

    SHORT_MIGRATE_REASON = {
        'NONE'          : 'none',
        'ERROR'         : 'erro',
        'STOP_RESUME'   : 'stop',
        'USER'          : 'user',
        'CANCEL'        : 'canc'
    }

    XML_TYPES = {
        'id'           : int,
        'uid'          : int,
        'name'         : str,
        'last_poll'    : int,
        'state'        : int,
        'lcm_state'    : int,
        'stime'        : int,
        'etime'        : int,
        'deploy_id'    : str,
        'memory'       : int,
        'cpu'          : int,
        'net_tx'       : int,
        'net_rx'       : int,
        'last_seq'     : int,
        'template'     : ET.tostring,
    }

    @staticmethod
    def allocate(client, template):
        vm_id = client.call(VirtualMachine.METHODS['allocate'], template)
        return vm_id

    def __init__(self, xml, client):
        super(VirtualMachine, self).__init__(xml, client)
        self.element_name = 'VM'
        self.id = self['ID'] if self['ID'] else None

    def deploy(self, host_id):
        self.client.call(self.METHODS['deploy'], self.id, host_id)

    def migrate(self, dest_host):
        self.client.call(self.METHODS['migrate'], self.id, dest_host, False)

    def live_migrate(self, dest_host):
        self.client.call(self.METHODS['migrate'], self.id, dest_host, True)

    def save_disk(self, disk_id, dest_disk):
        self.client.call(self.METHODS['savedisk'], self.id, disk_id, dest_disk)

    def shutdown(self):
        # Shutdowns an already deployed VM
        self._action('shutdown')

    def cancel(self):
        # Cancels a running VM
        self._action('cancel')

    def hold(self):
        # Sets a VM to hold state, scheduler will not deploy it
        self._action('hold')

    def release(self):
        # Releases a VM from hold state
        self._action('release')

    def stop(self):
        # Stops a running VM
        self._action('stop')

    def suspend(self):
        # Saves a running VM
        self._action('suspend')

    def resume(self):
        # Resumes the execution of a saved VM
        self._action('resume')

    def finalize(self):
        # Deletes a VM from the pool and DB
        self._action('finalize')

    def restart(self):
        # Resubmits the VM after failure
        self._action('restart')

    def _action(self, action):
        self.client.call(self.METHODS['action'], action, self.id)

    def __repr__(self):
        return '<oca.VirtualMachine("%s")>' % self.name

    @property
    def str_state(self):
        return self.VM_STATE[int(self.state)]

    @property
    def short_state(self):
        return self.SHORT_VM_STATES[self.str_state]

    @property
    def str_lcm_state(self):
        return self.LCM_STATE[int(self.lcm_state)]

    @property
    def short_lcm_state(self):
        return self.SHORT_LCM_STATES[self.str_lcm_state]


class VirtualMachinePool(Pool):
    METHODS = {
            'info' : 'vmpool.info',
    }

    def __init__(self, client):
        super(VirtualMachinePool, self).__init__('VM_POOL', 'VM', client)

    def factory(self, xml):
        vm = VirtualMachine(xml, self.client)
        vm.convert_types()
        return vm

    def __repr__(self):
        return '<oca.VirtualMachinePool()>'

