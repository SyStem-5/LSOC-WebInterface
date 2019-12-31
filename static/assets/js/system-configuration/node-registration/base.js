/* eslint-disable indent */
/* eslint-disable no-undef */

let lastNodeRegisterSubmit = ''

let zoneList = []

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_staff/node_registration')

    ws.addEventListener('open', function () {
        console.debug('Connected to staff node registration WS.')
    })
    ws.addEventListener('message', function (event) {
        var payload = JSON.parse(event.data)

        var command = payload.command

        var data = payload.data

        switch (command) {
        case 'ZonesGet':
            zoneList = data
            break
        case 'UnregedListNew':
            data = JSON.parse((data).replace(/[']/g, '"'))
            addToList(data)
            break
        case 'UnregedListGet':
            clearList()
            data.forEach(node => {
                addToList(node)
            })
            break
        case 'UnregedListOffline':
            console.warn(`Unregistered node went offline. ID: ${data}`)
            removeFromList(data)
            break
        case 'DiscoveryOn':
            if (payload['status']) {
                notification('', 'Node Discovery has been initiated.', 'info')
            } else {
                notification('|ERROR|', data, 'danger')
            }
            break
        case 'NodeRegister':
            if (payload['status']) {
                notification('', 'Node registration request was successfully sent.', 'info')
                $('#dynamicModal').modal('hide')
            } else {
                notification('|ERROR|', data, 'danger')
            }
            break
        case 'NodeRegisteredNew':
            removeFromList(data)

            if (data === lastNodeRegisterSubmit) {
                notification('', 'Node was successfully registered.', 'success')
                lastNodeRegisterSubmit = ''
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

function refreshUnregisteredList () {
    ws.send(JSON.stringify({
        type: 'unreged_list.get'
    }))
}

function sendNewNodeForm (data) {
    const payload = {}

    data.forEach(key => {
        payload[key['name']] = key['value']
    })

    ws.send(JSON.stringify({
        type: 'node.register',
        data: payload
    }))
}

function clearList () {
    document.getElementById('table-body').innerHTML = ''
}

function addToList (nodeData) {
    var tableBody = document.getElementById('table-body')

    var node = nodeData

    var item = document.createElement('tr')
    item.setAttribute('node', JSON.stringify(node))
    item.setAttribute('id', `node_${node.identifier}`)

    var itemCL1 = document.createElement('td')
    itemCL1.innerText = node.identifier
    item.appendChild(itemCL1)

    var elements = JSON.parse(node.elements)
    var itemCL2 = document.createElement('td')
    elements.forEach(element => {
        itemCL2.innerText += ' | ' + element.element_type
    })
    itemCL2.innerText += ' | '
    item.appendChild(itemCL2)

    tableBody.appendChild(item)

    $(`#node_${escapeHtml(node.identifier)}`).click(function () {
        generateModal($(this).attr('node'))
    })
}

function removeFromList (nodeID) {
    $(`#node_${nodeID}`).remove()
}

function generateModal (nodeObj) {
    const node = JSON.parse(nodeObj)
    const elements = JSON.parse(node.elements)

    let html = `
<div class="modal fade" id="dynamicModal" tabindex="-1" role="dialog" aria-labelledby="edit" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title" id="Heading">Register node ID: ${escapeHtml(node.identifier)}</h4>
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true"><span class="fas fa-times" aria-hidden="true"></span></button>
            </div>
            <div class="modal-body">
                <form id="form_register_${escapeHtml(node.identifier)}">
                    <input name="node_identifier" type="hidden" id="input_node_identifier" value="${escapeHtml(node.identifier)}">

                    <h5><b>General Settings</b></h5>

                    <div class="form-group">
                        <input name="node_name" class="form-control" type="text" placeholder="Node name" required>
                    </div>

                    <h5><strong>Element(s)</strong></h5>`

                    elements.forEach(element => {
                        html += `
                        <h6 class="indent-title"><strong>Address -></strong> ${escapeHtml(element.address)}</h6>
                        <h6 class="indent-title"><strong>Type -></strong>${element.element_type}</h6>
                        <input name="${escapeHtml(element.address)}:type" type="text" value="${element.element_type}" required hidden>
                        <div class="indent">
                            <div class="form-group">
                                <input name="${escapeHtml(element.address)}"
                                    class="form-control" type="text" placeholder="Name" required>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <label for="zone_dr:${escapeHtml(element.address)}">Zone</label>
                                    <select id="zone_dr:${escapeHtml(element.address)}" name="${escapeHtml(element.address)}:zone">
                                        <option value="-1"></option>
                                    `
                                        zoneList.forEach(zone => {
                                            html += `
                                                <option value="${escapeHtml(zone.id)}">${escapeHtml(zone.name)}</option>
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

                    html += `
                    <button type="submit" hidden/>
                </form>
            </div>
            <div class="modal-footer">
                <button id="btn_register_${escapeHtml(node.identifier)}" type="button" class="btn btn-warning btn-lg" style="width: 100%;">Register</button>
            </div>
        </div>
    </div>
</div>
`

    $('#dynamicModal').remove()

    $('body').append(html)

    $('#dynamicModal').modal('show')

    $(`#btn_register_${escapeHtml(node.identifier)}`).on('click', function () {
        var form = $(`#form_register_${escapeHtml(node.identifier)}`)

        for (let i = 0; i < form[0].length; i++) {
            if (!form[0][i].checkValidity()) {
                form.find(':submit').click()
                return
            }
        }

        lastNodeRegisterSubmit = node.identifier

        // If we're here, that means the form is valid and we can submit it to WSs!
        sendNewNodeForm(form.serializeArray())
    })
}

$(function ($) {
    $('#refresh_unregistered_list').on('click', function () {
        refreshUnregisteredList()
    })
})
