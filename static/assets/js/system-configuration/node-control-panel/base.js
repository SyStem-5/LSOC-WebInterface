/* eslint-disable indent */
/* eslint-disable no-undef */

let registeredNodes = {}
let zoneList = []

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_staff/node_control_panel')

    ws.addEventListener('open', function () {
        console.log('Connected to staff node control panel WS.')
    })
    ws.addEventListener('message', function (event) {
        var payload = JSON.parse(event.data)

        var command = payload.command

        var data = payload.data

        switch (command) {
            case 'ZonesGet':
                zoneList = data
                break
            case 'RegisteredListGet':
                registeredNodes = data
                populateList()
                break
            case 'NodeState':
                parsedData = JSON.parse(data)
                setNodeStateIndicator(parsedData['data'], parsedData['status'])
                break
            case 'NodeCommand':
                if (payload['status']) {
                    notification('', `Command '${data}' was successfully forwarded.`, 'info')
                } else {
                    notification('', 'Unable to forward the command to the system. Check the console for more info.', 'warning')
                    console.error(data)
                }
                break
            case 'NodeEdit':
                if (payload['status']) {
                    notification('', 'Node data change request was successfully sent.', 'info')
                } else {
                    notification('|Unable to edit node data|', payload['data'], 'danger')
                    console.error(data)
                }
                break
            case 'Error':
                notification('|Internal Error|', 'Please check the console.', 'danger')
                console.error(data)
                break
            default:
                console.log('Unknown command received:', command)
                break
        }
    })
    ws.addEventListener('close', function (event) {
        if (!event.wasClean) {
            var msg = 'WebSocket connection closed unexpectedly. Code: ' + event.code
            console.error(msg)

            notification('WebSockets error', msg, 'danger', false, 10)

            setTimeout(function () {
                WSInit()
            }, 5000)
        }
    })
}

WSInit()

function refreshNodesList () {
    ws.send(JSON.stringify({
        type: 'registeredlist.get'
    }))
}

function sendNodeCommand (command, nodeID) {
    ws.send(JSON.stringify({
        type: 'node.command',
        data: { command: command, data: nodeID }
    }))
}

function sendEditNodeForm (data) {
    const payload = {}

    data.forEach(key => {
        payload[key['name']] = key['value']
    })

    ws.send(JSON.stringify({
        type: 'node.edit',
        data: payload
    }))
}

function setNodeStateIndicator (identifier, state, retStyle = false) {
    state = state.toString()

    let style = ''
    let title = ''

    if (state === 'true') {
        style = 'background-color: green; max-width: 5px;'
        title = 'Online'
    } else if (state === 'false') {
        style = 'background-color: red; max-width: 5px;'
        title = 'Offline'
    } else {
        style = 'background-color: yellow; max-width: 5px;'
        title = 'Restarting'
    }

    if (!retStyle) {
        $(`#state-${identifier}`).attr('style', style)
        $(`#state-${identifier}`).attr('title', title)
    } else {
        return [style, title]
    }
}

$('#refresh_registered_list').on('click', function () {
    refreshNodesList()
})

function populateList () {
    var tableBody = document.getElementById('table-body')

    tableBody.innerHTML = ''

    if (registeredNodes === null | registeredNodes.length === 0) {
        return
    }

    registeredNodes.forEach(node => {
        var item = document.createElement('tr')
        item.setAttribute('id', `node-${node.identifier}`)
        item.setAttribute('node', JSON.stringify(node))

        var itemCL1 = document.createElement('td')
        itemCL1.setAttribute('id', `state-${node.identifier}`)

        var stateData = setNodeStateIndicator('', node.state, true)
        itemCL1.setAttribute('style', stateData[0])
        itemCL1.setAttribute('title', stateData[1])

        item.append(itemCL1)

        var itemCL2 = document.createElement('td')
        itemCL2.innerText = node.name
        item.append(itemCL2)

        var itemCL3 = document.createElement('td')
        itemCL3.innerText = node.identifier
        item.append(itemCL3)

        var itemCL5 = document.createElement('td')
        node.elements.forEach(element => {
            itemCL5.append(document.createTextNode(element.element_type + ' -> ' + element.name))
            itemCL5.append(document.createElement('br'))
        })
        item.append(itemCL5)

        tableBody.append(item)

        $(`#node-${node.identifier}`).click(function () {
            generateEditNodeModal($(this).attr('node'))
        })
    })
}

function generateEditNodeModal (node) {
    node = JSON.parse(node)
    var elements = node.elements

    var html = `
<div class="modal fade" id="dynamicModalNodeEdit" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header" style="display: unset">
                <h4 class="modal-title text-center">
                    <u>Node Settings</u>
                    <br>
                    <b>Name:</b> ${escapeHtml(node.name)}
                    <br>
                    <b>ID:</b> ${node.identifier}
                </h4>
            </div>
            <div class="modal-body">
                <form id="form-edit-node-${node.identifier}">
                    <input name="node_identifier" type="hidden" id="input_node_identifier" value="${node.identifier}">
                    <div class="form-group">
                        <input name="node_name" class="form-control" type="text" placeholder="Node name" id="input_node_name" value="${escapeHtml(node.name)}" required>
                    </div>

                    <h5><strong>Element(s)</strong></h5>
                    `

                    elements.forEach(element => {
                        html += `
                        <h6 class="indent-title"><strong>Address -></strong> ${escapeHtml(element.address)}</h6>
                        <h6 class="indent-title"><strong>Type -></strong> ${element.element_type}</h6>
                        <div class="indent">
                            <div class="form-group">
                                <input name="${escapeHtml(element.address)}"
                                    class="form-control" type="text" placeholder="Name" value="${escapeHtml(element.name)}" required>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <label for="zone_dr:${escapeHtml(element.address)}">Zone</label>
                                    <select id="zone_dr:${escapeHtml(element.address)}" name="${escapeHtml(element.address)}:zone">
                                        <option value="-1"></option>
                                    `

                                        zoneList.forEach(zone => {
                                            let isSelected = ''
                                            if (parseInt(element.zone) === zone.id) {
                                                isSelected = 'selected'
                                            }

                                            html += `
                                                <option value="${escapeHtml(zone.id)}" ${isSelected}>${escapeHtml(zone.name)}</option>
                                            `
                                        })
                        html += `
                                    </select>
                                </div>
                            </div>
                        </div>
                        <hr>
                        `
                    })
                    html += `<button type="submit" hidden/>
                </form>
            </div>
            <div class="modal-footer">
                <div class="dropdown">
                    <button class="btn btn-warning btn-lg dropdown-toggle" data-toggle="dropdown" aria-expanded="false" type="button">Commands</button>
                    <div role="menu" class="dropdown-menu">
                        <a role="presentation" class="dropdown-item btn_node_cmd_exec" href="#" data-cmd="restart">Restart</a>
                        <a role="presentation" class="dropdown-item btn_node_cmd_exec" href="#" data-cmd="unregister">Unregister</a>
                    </div>
                </div>
                <button id="btn-node-save-${node.identifier}" type="button" class="btn btn-info btn-lg" style="width: 100%;">Save</button>
            </div>
        </div>
    </div>
</div>
    `

    $('#dynamicModalNodeEdit').remove()
    $('body').append(html)

    $('#dynamicModalNodeEdit').modal('show')

    $(`#btn-node-save-${node.identifier}`).on('click', function () {
        var form = $(`#form-edit-node-${node.identifier}`)

        for (let i = 0; i < form[0].length; i++) {
            if (!form[0][i].checkValidity()) {
                form.find(':submit').click()
                return
            }
        }

        // If we're here, that means the form is valid and we can submit it to WSs!
        sendEditNodeForm(form.serializeArray())
    })

    $('.btn_node_cmd_exec').on('click', function () {
        processNodeCommands($(this).attr('data-cmd'), node.identifier)
    })
}

function processNodeCommands (data, nodeID) {
    switch (data) {
    case 'unregister':
        if (confirm('Unregister this node?')) {
            sendNodeCommand('unregister', nodeID)
        }
        break
    case 'restart':
        if (confirm('Restart this node?')) {
            sendNodeCommand('restart', nodeID)
        }
        break
    }
}
