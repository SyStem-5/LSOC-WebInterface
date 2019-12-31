/* eslint-disable indent */
/* eslint-disable no-undef */

(function ($) {
    'use strict' // Start of use strict

    $('#load-node_registration').on('click', function () {
        load('/staff/system_configuration/nodes/registration')
    })

    $('#load-node_control_panel').on('click', function () {
        load('/staff/system_configuration/nodes/CP')
    })

    $('#load-zone_management').on('click', function () {
        load('/staff/system_configuration/zones')
    })

    $('#load-account_management').on('click', function () {
        load('/staff/system_configuration/accounts')
    })

    function load (link) {
        window.location.href = link
    }
})(jQuery) // End of use strict

/* TEMPORARY */
const wanIPLabel = $('#label-wanip')
const wanIPLabelToggle = $('#btn-wanip-toggle')

const updateStateLabel = $('#label-update-status')
const updateLogTextArea = $('#update-log-text')
const updateChangelogTextArea = $('#update-changelog-text')
const updateButtonShowChangelogInstall = $('#btn-update-changelog-install')
const updateButtonDlAndInstall = $('#btn-update-dl_install')
const updateLogButton = $('#btn-update-log')

let logRequestID = ''
const permanentComponents = ['component-mqtt', 'component-blackbox']
const trackedComponents = ['component-mqtt', 'component-blackbox']
const operationalLabel = 'Operational'
const partiallyOperationalLabel = 'Partially Operational'
const notOperationalLabel = 'Not Operational'

const refreshedLabel = $('#status-header-refreshlabel')
let timeElapsed = 0
const timeIncrements = 60
let timer

function setTimer () {
    if (timer) {
        clearInterval(timer)
    }

    timer = setInterval(updateRefreshedLabel, timeIncrements * 1000)
    timeElapsed = 0
    refreshedLabel.text('Refreshed less than 1 minute ago')
}

/* TEMPORARY */
wanIPLabelToggle.on('click', function () {
    wanIPLabel.toggle('fast')
})
wanIPLabelToggle.click()

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_staff/system_status')

    ws.addEventListener('open', function () {
        console.debug('Connected to staff system configuration WS.')
    })
    ws.addEventListener('message', function (event) {
        const payload = JSON.parse(event.data)

        const command = payload.command

        const data = payload.data

        switch (command) {
            /* TEMPORARY */
            case 'SystemIP':
                wanIPLabel.text(data)
                break
            case 'SystemStatus':
                if (data['component'] === 'neco') {
                    necoTracking(data['data'])
                } else {
                    // If the component is not in the array, just do nothing
                    // This works because NECO is tracked differently
                    if (trackedComponents.includes(`component-${data['component']}`)) {
                        updateComponentState(data)
                    }
                }

                if (data['component'] === 'mqtt' && !data['state']) {
                    stateGlobalOffline()
                }

                updateHeader()
                break
            case 'ComponentLog':
                // Check if the request ID matches ours
                if (data['request'] === logRequestID) {
                    const txtArea = $('#component-log-text')

                    txtArea.val(data['data'])
                    // Scroll to the bottom as soon as we load
                    txtArea.scrollTop(txtArea[0].scrollHeight)
                }
                break
            case 'UpdateState':
                // Check if the "show log" link is shown and show it if its hidden
                updateLogButton.show()

                // Append the data received to the log textarea
                updateLogTextArea.append(data + '\n')

                updateStateLabel.text(data)
                break
            case 'UpdateChangelog':
                // Show the "show changelog & install" button
                updateButtonShowChangelogInstall.show()

                updateChangelogTextArea.val(
                    updateChangelogTextArea.val() + data + '\n'
                )
                break
            case 'UpdateStart':
                updateButtonShowChangelogInstall.hide()
                break
            case 'SystemShutdown':
                if (payload['status']) {
                    notification('|System|', 'Shutting down...')
                } else {
                    notification('|Error|', 'Could not send shutdown command.', 'warning')
                    console.warn(data)
                }
                break
            case 'SystemReboot':
                if (payload['status']) {
                    notification('|System|', 'Rebooting...')
                } else {
                    notification('|Error|', 'Could not send reboot command.', 'warning')
                    console.warn(data)
                }
                break
            case 'Error':
                notification('|Internal Error|', 'Please check the console.', 'danger')
                console.error(data)
                break
            default:
                console.log('Unknown command received:', command)
                console.log(data)
                break
        }
    })
    ws.addEventListener('close', function (event) {
        if (!event.wasClean) {
            const msg = `WebSocket connection closed unexpectedly. Code: ${event.code}`
            console.error(msg)

            notification('WebSockets error', msg, 'danger', false, 10)

            // If we lose the connection to WSs, assume everything is down
            stateGlobalOffline()
            updateHeader()

            setTimeout(function () {
                WSInit()
            }, 5000)
        }
    })
}

WSInit()

function stateGlobalOffline () {
    trackedComponents.forEach(component => {
        // This check is here so we can remove the NECO listing if ws disconnects
        if (permanentComponents.includes(component)) {
            const obj = $(`#${component}`)
            obj.text(notOperationalLabel)
            obj.removeClass('badge-info badge-success badge-warning badge-danger')
            obj.addClass('badge-danger')
        } else {
            $(`#${component.replace('component', 'obj')}`).remove()
        }
    })
}

function updateRefreshedLabel () {
    let text = ''
    timeElapsed += timeIncrements

    if (timeElapsed < 60) {
        text = 'Refreshed less than 1 minute ago'
    } else if (timeElapsed < 120) {
        text = 'Refreshed 1 minute ago'
    } else if (timeElapsed < 3600) {
        text = `Refreshed ${Math.floor(timeElapsed / 60)} minutes ago`
    } else {
        let letter = ''
        if (Math.floor(timeElapsed / (60 * 60)) !== 1) { letter = 's' }

        text = `Refreshed ${Math.floor(timeElapsed / (60 * 60))} hour${letter} ago`
    }

    refreshedLabel.text(text)
}

function updateHeader () {
    const classes = 'bg-info bg-success bg-warning bg-danger'
    const states = []

    setTimer()

    trackedComponents.forEach(component => {
        states.push($(`#${component}`).text())
    })

    const obj = $('#status-header')
    const objText = $('#status-header-text')

    if (states.includes(operationalLabel) & states.includes(notOperationalLabel) | states.includes(partiallyOperationalLabel)) {
        obj.removeClass(classes)
        obj.addClass('bg-warning')

        objText.text('System not fully operational')
    } else if (states.includes(notOperationalLabel)) {
        obj.removeClass(classes)
        obj.addClass('bg-danger')

        objText.text('System is not operational')
    } else {
        obj.removeClass(classes)
        obj.addClass('bg-success')

        objText.text('System is fully operational')
    }
}

function updateComponentState (data) {
    const classes = 'badge-info badge-success badge-warning badge-danger'
    const obj = $(`#component-${data['component']}`)

    if (data['state']) {
        obj.text(operationalLabel)

        obj.removeClass(classes)
        obj.addClass('badge-success')
    } else {
        obj.text(notOperationalLabel)

        obj.removeClass(classes)
        obj.addClass('badge-danger')
    }
}

function makeID (length = 12) {
    let result = ''
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    const charactersLength = characters.length

    for (let i = 0; i < length; i++) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength))
    }

    return result
 }

// eslint-disable-next-line no-unused-vars
function requestNECOStates () {
    ws.send(JSON.stringify({
        type: 'neco.states'
    }))
}

// This is used in the necoTracking function - DOM generation
// eslint-disable-next-line no-unused-vars
function requestComponentLog (data) {
    // Generate a random request ID and save it to a variable
    logRequestID = makeID()
    const payload = {
        id: data.attr('data-necoid'),
        request: logRequestID,
        component: data.attr('data-component')
    }

    ws.send(JSON.stringify({
        type: 'component.log',
        data: payload
    }))
}

function necoTracking (data) {
    const badgeClasses = 'badge-info badge-success badge-warning badge-danger'
    const states = []

    // If the NECO with that ID doesn't exist, create the list item
    if (!$(`#obj-${data['id']}`).length) {
        let html = `<div id="obj-${data['id']}" class="list-group-item">
                        <h4 class="list-group-item-heading" title="NECO ID: '${data['id']}'"
                            data-necoid="${data['id']}"
                            data-component="NeutronCommunicator - Service"
                            onClick="requestComponentLog($(this)); loadLog($(this));">
                            Neutron Communicator
                            <a href="javascript:void(0);" data-toggle="tooltip" data-placement="bottom" title="Component used for maintaining system security.">
                                <i class="fa fa-question-circle"></i>
                            </a>

                        </h4>
                        <a href="javascript:void(0);" onClick="requestNECOStates()" data-toggle="tooltip" data-placement="bottom" title="Refresh NECO component states">
                                <i class="fa fa-refresh float-right"></i>
                            </a>
                        <p class="list-group-item-text"><span id="component-${data['id']}" class="badge badge-info">...</span></p>

                        <div>
                            <a class="btn btn-outline-primary btn-block btn-sm" data-toggle="collapse" aria-expanded="false" aria-controls="collapse-${data['id']}" href="#collapse-${data['id']}" role="button">
                                <i class="fas fa-angle-down"></i>
                            </a>
                            <div class="collapse" id="collapse-${data['id']}">
                                <br>`
                                data['components'].forEach(component => {
                                    states.push(component.state)

                                    stateClass = ''
                                    stateLabel = ''

                                    if (component.state) {
                                        stateClass = 'badge-success'
                                        stateLabel = 'Online'
                                    } else {
                                        stateClass = 'badge-danger'
                                        stateLabel = 'Offline'
                                    }

                                    html += `
                                        <button class="btn"
                                            data-necoid="${data['id']}"
                                            data-component="${component.component}"
                                            onClick="requestComponentLog($(this)); loadLog($(this));"
                                            data-toggle="modal" data-target="#modal-component-log">
                                            <p>
                                                <span id="component-${data['id']}-${(component.component).replace(/ /g, '_')}" class="badge ${stateClass}">${stateLabel}</span>
                                                ${component.component}
                                                <span id="component-${data['id']}-${(component.component).replace(/ /g, '_')}-version" class="badge badge-info">${component.version}</span>
                                            </p>
                                        </button>
                                        <br>`
                                })
        html += `           </div>
                        </div>
                    </div>`

        $('#list-component').append(html)

        // Append it to the main tracker so that the header can get the state data
        if (!trackedComponents.includes(`component-${data['id']}`)) {
            trackedComponents.push(`component-${data['id']}`)
         } // else {
        //     console.log('Skipping adding neco component to the tracking array.')
        // }
    } else {
        data['components'].forEach(component => {
            states.push(component.state)
            const obj = $(`#component-${data['id']}-${(component.component).replace(/ /g, '_')}`)

            // Always update the version badge
            $(`#component-${data['id']}-${(component.component).replace(/ /g, '_')}-version`).text(component.version)

            if (component.state) {
                obj.text('Online')

                obj.removeClass(badgeClasses)
                obj.addClass('badge-success')
            } else {
                obj.text('Offline')

                obj.removeClass(badgeClasses)
                obj.addClass('badge-danger')
            }
        })
    }

    // Here we determine the neco state by comparing the states of its components
    obj = $(`#component-${data['id']}`)
    if (states.includes(true) && states.includes(false)) {
        obj.removeClass(badgeClasses)
        obj.addClass('badge-warning')
        obj.text(partiallyOperationalLabel)
    } else if (states.includes(false)) {
        obj.removeClass(badgeClasses)
        obj.addClass('badge-danger')
        obj.text(notOperationalLabel)
    } else {
        obj.removeClass(badgeClasses)
        obj.addClass('badge-success')
        obj.text(operationalLabel)
    }
}

// eslint-disable-next-line no-unused-vars
function loadLog (data) {
    $('#component-log-text').val('_O_o__LOADING__o_O_')
    $('#component-log-title').text(`${data.attr('data-component')} Log`)

    $('#component-log-refreshbtn').attr('data-necoid', data.attr('data-necoid'))
    $('#component-log-refreshbtn').attr('data-component', data.attr('data-component'))

    $('#modal-component-log').modal()
}

// As soon as the modal is displayed, scroll to the bottom
$('#modal-component-log').on('shown.bs.modal', function () {
    const txtArea = $('#component-log-text')
    txtArea.scrollTop(txtArea[0].scrollHeight)
})

$('#btn-update-refresh').on('click', function () {
    // Clear the changelog textarea
    updateChangelogTextArea.val('')

    if (updateLogTextArea.val().length !== 0) {
        updateLogTextArea.append('\n')
    }

    ws.send(JSON.stringify({
        type: 'update.check'
    }))
})

updateButtonDlAndInstall.on('click', function () {
    if (confirm('The Web Interface might be restarted as a part of the system update.\n\nContinue?')) {
        // Hide the changelog modal
        $('#modal-update-changelog').modal('hide')

        // Show the log modal
        $('#modal-update-log').modal('show')

        ws.send(JSON.stringify({
            type: 'update.start'
        }))
    }
})

$('#system_mng-shutdown').on('click', function () {
    if (confirm('The system is going to shutdown in about 30sec if you continue.\n\nContinue?')) {
        ws.send(JSON.stringify({
            type: 'system_mng.shutdown'
        }))
    }
})

$('#system_mng-reboot').on('click', function () {
    if (confirm('The system is going to reboot in about a minute if you continue.\n\nContinue?')) {
        ws.send(JSON.stringify({
            type: 'system_mng.reboot'
        }))
    }
})
