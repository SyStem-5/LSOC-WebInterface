/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

function basicswitch (nodeIdentifier, elementIdentifier, data) {
    const elem = $(`#${nodeIdentifier}-${elementIdentifier}`)

    const nodeID = elem.attr('data-nodeid')
    const elementID = elem.attr('data-elementid')

    // This is a test for different color shadow
    if (elem.is('.shadow') && (elementID === '0xtest_address1' && nodeID === 'regl4LD0X946d')) {
        elem.css('-webkit-box-shadow', '0 0 20px #ff00fb')
        elem.css('box-shadow', '0 0 20px #ff00fb')
    }

    elem.removeClass('shadow colored-shadow')

    if (data === 'true') {
        elem.addClass('colored-shadow')
    } else {
        elem.addClass('shadow')
    }
}

function thermostat (nodeIdentifier, elementIdentifier, data) {
    const elem = $(`#${nodeIdentifier}-${elementIdentifier}`)

    // Set the label with the data received
    elem.text(data)
}

function dht11 (nodeIdentifier, elementIdentifier, data) {
    const elemData = JSON.parse(data)

    const elem1 = $(`#temp-${nodeIdentifier}-${escapeHtml(elementIdentifier)}`)
    const elem2 = $(`#hum-${nodeIdentifier}-${escapeHtml(elementIdentifier)}`)

    elem1.text(elemData.temp)
    elem2.text(elemData.hum)
}
