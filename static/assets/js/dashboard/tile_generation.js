/* eslint-disable no-irregular-whitespace */
/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

const tileRow = $('#row-tiles')

function generateTile (typeFunction) {
    tileRow.append(typeFunction)
}

function tileBasicSwitch (data, disabled) {
    let state

    // Node offline-online
    if (disabled) {
        state += ' element-disabled'
    } else {
        state += ' basicswitch'
    }

    return `
    <div class="col-12 col-sm-3 col-lg-2 col-lightswitch unselectable">
        <div id="${data.node_identifier}-${escapeHtml(data.address)}" class="card shadow ${state}"
            data-nodeid="${data.node_identifier}" data-elementid="${escapeHtml(data.address)}">
            <div class="card-body">
                <i class="far fa-lightbulb d-flex justify-content-center" style="font-size: 42px;"></i>
                <span class="d-flex justify-content-center" style="margin-top: 10px;">${escapeHtml(data.name)}</span>
            </div>
        </div>
    </div>
    `
}

function tileThermostat (data, disabled) {
    let state = ''

    let controls = ''
    let btnStates = ''

    if (disabled) {
        state = 'element-disabled'
        btnStates = 'disabled'
    } else {
        controls = 'thermostat'
    }

    return `
    <div class="col-12 col-sm-3 col-thermostat">
        <div class="card shadow ${state}">
            <div class="card-body unselectable">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-center">
                            <span id="${data.node_identifier}-${escapeHtml(data.address)}"
                                class="text-nowrap text-success">${escapeHtml(data.data)}</span>
                            <strong>°C</strong>
                        </div>
                    </div>
                </div>
                <div class="row align-items-center">
                    <div class="col text-center">
                        <button class="btn ${controls} thermostat-up" type="button"
                            data-nodeid="${data.node_identifier}" data-elementid="${escapeHtml(data.address)}" ${btnStates}>
                            <i class="fas fa-angle-up"></i>
                        </button>
                        <button class="btn ${controls} thermostat-down" type="button"
                            data-nodeid="${data.node_identifier}" data-elementid="${escapeHtml(data.address)}" ${btnStates}>
                            <i class="fas fa-angle-down"></i>
                        </button>
                    </div>
                </div>
                <span class="d-flex justify-content-center" style="margin-top: 5px;">${escapeHtml(data.name)}</span>
            </div>
        </div>
    </div>
    `
}

function tileDHT11 (data, disabled) {
    const elemData = JSON.parse(data.data)

    let state = ''

    // Node offline-online
    if (disabled) {
        state = 'element-disabled'
    }

    return `
    <div class="col-12 col-sm-2 col-lg-3 col-dht11">
        <div class="card shadow ${state}">
            <div class="card-body unselectable">
                <div class="row">
                    <div class="col d-inline-flex justify-content-center align-items-center d-flex">
                        <i class="fas fa-thermometer-half justify-content-center" style="font-size: 39px;color: #27ff97;"></i>
                        <div style="margin-left: 10px;"></div>
                        <span id="temp-${data.node_identifier}-${escapeHtml(data.address)}">${escapeHtml(elemData.temp)}</span>
                        <strong> °C</strong>
                    </div>
                    <div class="col d-inline-flex justify-content-center align-items-center d-flex">
                        <i class="icon ion-waterdrop justify-content-center" style="font-size: 39px;color: #5869ff;"></i>
                        <div style="margin-left: 10px;"></div>
                        <span id="hum-${data.node_identifier}-${escapeHtml(data.address)}">${escapeHtml(elemData.hum)}</span>
                        <strong> %</strong>
                    </div>
                </div>
                <span class="text-nowrap d-flex justify-content-center" style="margin-top: 10px;">${escapeHtml(data.name)}</span>
            </div>
        </div>
    </div>
    `
}
