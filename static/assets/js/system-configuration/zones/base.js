/* eslint-disable no-undef */

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_staff/zones')

    ws.addEventListener('open', function () {
        console.debug('Connected to staff zones WS.')
    })
    ws.addEventListener('message', function (event) {
        var payload = JSON.parse(event.data)

        var command = payload.command

        var data = payload.data

        switch (command) {
            case 'ZonesGet':
                populateTable(data)
                break
            case 'ZoneAdd':
                if (data.state) {
                    notification('New zone:', `'${data['data']}'`, 'success')
                } else {
                    notification('Could not add a new zone', data['data'], 'danger')
                }
                break
            case 'ZoneRemove':
                if (data.state) {
                    notification('Removed zone:', `'${data['data']}'`, 'success')
                } else {
                    notification('Could not remove zone', data['data'], 'danger')
                }
                break
            case 'ZoneEdit':
                if (data.state) {
                    notification('Edited zone:', `'${data['data']}'`, 'success')
                } else {
                    notification('Could not edit zone', data['data'], 'danger')
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

const tableBody = $('#table-body')
const btnAddRow = $('#btn-add-row')

$('tbody').on('click', '.remove-unsaved-row', function () {
    $(this).parent('td').parent('tr').remove()
    toggleAddRowBtn(true)
})

$('tbody').on('click', '.add-unsaved-row', function () {
    const form = $(this).parent('td').parent('tr').children('td').children('form')

    if (!form[0].checkValidity()) {
        form.find(':submit').click()
    } else {
        addNewZone(form.serializeArray())

        toggleAddRowBtn(true)
    }
})

$('tbody').on('click', '.save-edited-row', function () {
    const form = $(this).parent('td').parent('tr').children('td').children('form')

    if (!form[0].checkValidity()) {
        form.find(':submit').click()
    } else {
        editZone(form.serializeArray())
        toggleAddRowBtn(true)
    }
})

$('tbody').on('click', '.remove-saved-row', function () {
    const zoneID = $(this).parent('td').parent('tr').attr('id')

    removeZone(zoneID)

    toggleAddRowBtn(true)
})

$('tbody').on('click', '.edit-saved-row', function () {
    toggleAddRowBtn(false)

    // Convert the 'Zone name' column to a form with an input
    const parent = $(this).parent('td').parent('tr')
    const child = parent.children('td')

    convertToEdit(parent, child)
})

function convertToEdit (parent, child) {
    const id = parent.attr('id')
    const name = $(child[0]).text()

    $(child[0]).html(
        `
        <form>
            <input id="new_zone_input" name="zone_name" placeholder="Name" value="${name}" required></input>
            <input name="zone_id" value="${id}" required hidden></input>
            <button hidden type="submit"/>
        </form>
        `
    )

    $(child[1]).html(
        `
        <button class="btn save-edited-row" type="button">
            <i class="fas fa-save"></i>
        </button>
        <button class="btn btn-sm remove-saved-row" type="button">
            <i class="fas fa-trash-alt"></i>
        </button>
        `
    )
}

function getZones () {
    ws.send(JSON.stringify({
        type: 'zones.get'
    }))
}

function addNewZone (data) {
    const payload = {}
    data.forEach(element => {
        payload[element.name] = element.value
    })

    ws.send(JSON.stringify({
        type: 'zone.add',
        data: payload
    }))

    // Request for an updated list
    getZones()
}

function removeZone (zoneID) {
    ws.send(JSON.stringify({
        type: 'zone.remove',
        data: zoneID
    }))

    // Request for an updated list
    getZones()
}

function editZone (data) {
    const payload = {}
    data.forEach(element => {
        payload[element.name] = element.value
    })

    ws.send(JSON.stringify({
        type: 'zone.edit',
        data: payload
    }))

    // Request for an updated list
    getZones()
}

btnAddRow.on('click', function () {
    const elem = addRow()

    toggleAddRowBtn(false)

    // Scroll to the bottom of the table
    $('html, body').animate({
        scrollTop: $(elem).offset().top
    }, 250)

    $('#new_zone_input').focus()
})

function toggleAddRowBtn (state) {
    if (state) {
        btnAddRow.removeAttr('disabled')
        btnAddRow.removeAttr('title')
    } else {
        btnAddRow.attr('disabled', '')
        btnAddRow.attr('title', 'You\'re already editing a row.')
    }
}

function addRow () {
    const html = `
    <tr>
        <td class="border rounded-0" >
            <form>
                <input id="new_zone_input" name="zone_name" placeholder="Name" required></input>
                <button hidden type="submit"/>
            </form>
        </td>
        <td class="d-flex justify-content-center">
            <button class="btn add-unsaved-row" type="button">
                <i class="fas fa-save"></i>
            </button>
            <button class="btn btn-sm remove-unsaved-row" type="button">
                <i class="far fa-window-close"></i>
            </button>
        </td>
    </tr>
    `

    return tableBody.append(html)
}

function populateTable (data) {
    // Empty the table body
    tableBody.html('')

    data.forEach(zone => {
        const html = `
        <tr id=${escapeHtml(zone.id)}>
            <td class="border rounded-0">
                ${escapeHtml(zone.name)}
            </td>
            <td class="d-flex align-items-center">
                <button class="btn edit-saved-row" type="button">
                    <i class="far fa-edit"></i>
                </button>
                <button class="btn btn-sm remove-saved-row" type="button">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        </tr>
        `

        tableBody.append(html)
    })
}
