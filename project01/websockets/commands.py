
from enum import Enum

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class WSLSOC(Enum):
    # TEMPORARY
    SystemIP = "system.ip"

    # (NECO) => WI - client
    SystemStatus = "system.status"
    # Client => NECO
    NECOStates = "neco.states"
    # Client <=> NECO
    ComponentLog = "component.log"
    UpdateStart = "update.start"
    # Client => NECO
    UpdateCheck = "update.check"
    # NECO => Client
    UpdateState = "update.state"
    UpdateChangelog = "update.changelog"

    # BlackBox
    NodeState = "node.state"
    UnregedListGet = "unreged_list.get"
    UnregedListNew = "unreged_list.new"
    UnregedListOffline = "unreged_list.offline"
    DiscoveryOn = "discovery.on"
    DiscoveryOff = "discovery.off"
    NodeRegister = "node.register"
    NodeRegisteredNew = "node.registered"
    RegisteredListGet = "registeredlist.get"
    NodeCommand = "node.command"
    NodeEdit = "node.edit"

    # WebInterface
    ZonesGet = "zones.get"
    ZoneAdd = "zone.add"
    ZoneRemove = "zone.remove"
    ZoneEdit = "zone.edit"

    # Nodes
    ElementSet = "element.set"
    ElementState = "element.state"

    # System Control
    SystemShutdown = "system_mng.shutdown"
    SystemReboot = "system_mng.reboot"

class AccountManagement(Enum):
    AccountRegister = "account.register"
    AccountEdit = "account.edit"
    AccountRemove = "account.remove"


def new(cmd_type, data):
    ret = {}
    ret["data"] = data
    ret["command"] = cmd_type.name

    return ret


def new_bare(cmd_type, data):
    data["command"] = cmd_type.name
    return data


def element_update_send(group, data):
    async_to_sync(get_channel_layer().group_send)(
        group,
        {"type": WSLSOC.ElementState.value,
            "command": WSLSOC.ElementState.name, "data": data}
    )
