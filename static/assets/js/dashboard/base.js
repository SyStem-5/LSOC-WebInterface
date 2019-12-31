/* eslint-disable no-undef */

let registeredList

const registeredElements = {}

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_user/dashboard')

    ws.addEventListener('open', function () {
        console.debug('Connected to user WS.')
    })
    ws.addEventListener('message', function (event) {
        var payload = JSON.parse(event.data)

        var command = payload.command

        var data = payload.data

        switch (command) {
            case 'RegisteredListGet':
                registeredList = JSON.parse(data)
                refreshTiles()
                break
            case 'ElementSet':
                if (!data.status) {
                    notification('Element set error', data.data, 'danger')
                }
                break
            case 'ElementState':
                try {
                    const dataSplit = data.split('::')
                    registeredElements[`${dataSplit[0]}-${dataSplit[1]}`](dataSplit[0], dataSplit[1], dataSplit[2])
                } catch (error) {}
                break
            case 'Error':
                notification('|Internal Error|', 'Please check the console.', 'danger')
                console.error(data)
                break
            default:
                console.log('Unknown command received:', command)
                // console.log(data)
                break
        }
    })
    ws.addEventListener('close', function (event) {
        if (!event.wasClean) {
            const msg = `WebSocket connection closed unexpectedly. Code: ${event.code}`
            console.error(msg)

            notification('WebSockets error', msg, 'danger', false, 10)

            setTimeout(function () {
                WSInit()
            }, 5000)
        }
    })
}

WSInit()

function refreshTiles () {
    tileRow.html('')

    registeredList.forEach(node => {
        node.elements.forEach(element => {
            try {
                switch (element.element_type) {
                    case 'BasicSwitch':
                        // Register the control so we know where to go when setting received state
                        registeredElements[`${node.identifier}-${element.address}`] = basicswitch

                        generateTile(tileBasicSwitch(element, !node.state))

                        // Set the tile state
                        basicswitch(node.identifier, element.address, element.data)
                        break
                    case 'Thermostat':
                        // Register the control so we know where to go when setting received state
                        registeredElements[`${node.identifier}-${element.address}`] = thermostat

                        generateTile(tileThermostat(element, !node.state))
                        break
                    case 'DHT11':
                        registeredElements[`${node.identifier}-${element.address}`] = dht11

                        generateTile(tileDHT11(element, !node.state))
                        break
                    default:
                        console.warn(`Unknown element type: '${(element.element_type).toString()}'`)
                        break
                }
            } catch (e) {
                notification('Tile Generation Error', 'Please check the console for more information.', 'danger')

                console.error('Tile generation error')
                console.error(e)
            }
        })
    })
}

function elementSetSend (nodeID, elementID, elementType, data) {
    const payload = {}

    payload['node_identifier'] = nodeID
    payload['element_identifier'] = elementID
    payload['element_type'] = elementType
    payload['data'] = data

    ws.send(JSON.stringify({
        type: 'element.set',
        data: payload
    }))
}

$(document).on('click', '.basicswitch', function () {
    const elem = $(this)

    const nodeID = elem.attr('data-nodeid')
    const elementID = elem.attr('data-elementid')

    const state = (!elem.is('.colored-shadow')).toString()
    elementSetSend(nodeID, elementID, 'BasicSwitch', state)
})

$(document).on('click', '.thermostat', function () {
    const elem = $(this)

    const nodeID = elem.attr('data-nodeid')
    const elementID = elem.attr('data-elementid')

    const data = elem.is('.thermostat-up') ? '+' : '-'
    elementSetSend(nodeID, elementID, 'Thermostat', data)
})
