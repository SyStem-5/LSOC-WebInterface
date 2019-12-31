/* eslint-disable indent */
/* eslint-disable no-undef */

let nodeElementList = {}
let dict = {}

let lastRemovedAccount = ''

let ws

function WSInit () {
    ws = new WebSocket(
        (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host +
        '/ws_staff/account_management')

    ws.addEventListener('open', function () {
        console.debug('Connected to staff account management WS.')
    })
    ws.addEventListener('message', function (event) {
        var payload = JSON.parse(event.data)

        var command = payload.command

        var data = payload.data

        switch (command) {
            case 'AccountRegister':
                if (payload['status']) {
                    notification('', 'A new account has been successfully registered.', 'success')
                    $('#modalAddUser').modal('hide')
                } else {
                    notification('|Failed to register the new account|', payload['data'], 'danger')
                    $('#form-errors_register').html(payload['data'])
                    $('#form-errors_register').find('input').remove()
                    $('#form-errors_register').find('.helptext').remove()
                }
                break
            case 'AccountEdit':
                if (payload['status']) {
                    notification('', 'Changes were successfully saved.', 'success')
                    $('#dynamicModal').modal('hide')
                } else {
                    notification('', 'Failed to save the account data.', 'danger')
                    $('#form-errors_edit').html(payload['data'])
                    $('#form-errors_edit').find('input').remove()
                    $('#form-errors_edit').find('.helptext').remove()
                }
                break
            case 'AccountRemove':
                if (payload['status']) {
                    notification('', 'Account was successfully removed.', 'success')

                    $(`#${lastRemovedAccount}`).remove()
                    lastRemovedAccount = ''

                    $('#dynamicModal').modal('hide')
                } else {
                    notification('', 'Failed to remove the account.', 'danger')
                    $('#form-errors_edit').html(payload['data'])
                    $('#form-errors_edit').find('input').remove()
                    $('#form-errors_edit').find('.helptext').remove()
                }
                break
            case 'RegisteredListGet':
                nodeElementList = data
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

$(function () {
    $('ul.checktree').checktree()
})

$('tr[id^="user:"]').on('click', function (data) {
    // Open a modal for editing the account information
    createEditAccountModal(this)
})

function generateACLModal () {
    let html = `
    <div class="modal fade" role="dialog" tabindex="-1" style="z-index: 1051" id="modalNodeACL">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h4 class="modal-title">Node Access Control List</h4>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
                <div class="modal-body">
                    <ul class="checktree">
                        <li>
                            <input id="all_nodes" type="checkbox" /><label for="all_nodes">Nodes</label>
                            <ul>`
                                nodeElementList.forEach(node => {
                                    let subHtml = `
                                    <li>
                                        <input id="${escapeHtml(node.identifier)}" type="checkbox" />
                                        <label style="display: contents !important;"
                                                for="${escapeHtml(node.identifier)}"
                                                title="ID: ${escapeHtml(node.identifier)}">
                                                &nbsp${escapeHtml(node.name)}
                                        </label>
                                        <ul>`
                                            node.elements.forEach(element => {
                                                subHtml += `
                                                <li>
                                                    <input id="${element.node_identifier}:${escapeHtml(element.address)}"
                                                        type="checkbox" />
                                                    <label style="display: contents !important;"
                                                            for="${element.node_identifier}:${escapeHtml(element.address)}"
                                                            title="Address: ${escapeHtml(element.address)}">
                                                        &nbsp${escapeHtml(element.element_type)} - ${escapeHtml(element.name)}
                                                    </label>
                                                </li>
                                                `
                                            })
                            subHtml += `</ul>
                                    </li>
                                    `

                                    html += subHtml
                                })
                    html += `</ul>
                        </li>
                    </ul>
                </div>
                <div class="modal-footer">
                    <button id="btn-save-acl" type="button" class="btn btn-primary btn-block" data-dismiss="modal">Save</button>
                </div>
            </div>
        </div>
    </div>
    `

    $('body').append(html)

    $('#btn-save-acl').on('click', function () {
        $('#lsoc_permissions').val(JSON.stringify(dict))
    })
}

function createEditAccountModal (data) {
    var username = $(data).attr('data-username')
    var email = $(data).attr('data-email')
    var lsocPermissions = $(`#${username}\\:permission_data`).html()
    var description = $(data).attr('data-description')

    $('#modalNodeACL').remove()
    generateACLModal()

    const html = `
<div class="modal fade" id="dynamicModal" tabindex="-1" role="dialog" aria-labelledby="edit" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title" id="Heading">Edit account <br> User: '${username}'</h4>
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true"><span class="fas fa-times" aria-hidden="true"></span></button>
            </div>
            <div class="modal-body">
                <form id="form-edit-user-${username}">

                    <div class="row" style="width: 95%; display: block;">
                        <div class="column" style="margin-left: 50px;">

                            <input value="${username}" type="text" name="username" class="form-control" maxlength="254" autofocus="" required="" id="username" hidden>

                            <div class="row" style="margin-bottom: 5px;">
                                <input value="${email}" type="email" name="email" class="form-control" placeholder="E-mail address" maxlength="254" required id="id_email">
                            </div>

                            <div class="row" style="margin-bottom: 5px;">
                                <input type="password" name="old_password" class="form-control" placeholder="Old password" id="id_old_password">
                            </div>

                            <div class="row" style="margin-bottom: 5px;">
                                <input type="password" name="new_password1" class="form-control" placeholder="New Password" id="id_new_password1">
                            </div>
                            <div class="row" style="margin-bottom: 5px;">
                                <input type="password" name="new_password2" class="form-control" placeholder="Confirm Password" id="id_new_password2">
                            </div>

                            <div class="row" style="margin-bottom: 5px;">
                                <div style="width: 73%;">
                                    <input value="${lsocPermissions}" type="text" name="lsoc_permissions" class="form-control" value="{}" required id="lsoc_permissions" readonly="readonly">
                                </div>
                                <!-- This button opens a modal that lists nodes and their elements with checkmarks by their side -->
                                <button id="btn-node-acl-${username}" type="button" class="btn btn-outline-warning" style="display: inline-block;" data-toggle="modal" data-target="#modalNodeACL">
                                    Node ACL
                                </button>
                            </div>

                            <div class="row" style="margin-bottom: 5px;">
                                <input value="${description}" type="text" name="description" class="form-control" placeholder="Living room device." maxlength="100" required id="id_description">
                            </div>

                            <button type="submit" hidden/>
                        </div>
                    </div>
                </form>
                <div id="form-errors_edit" style="color: red;"></div>
            </div>
            <div class="modal-footer">
                <button id="btn-remove-account-${username}" type="button" class="btn btn-danger btn-lg" style="width: 100%;">Remove Account</button>
                <button id="btn-save-account-${username}" type="button" class="btn btn-warning btn-lg" style="width: 100%;">Save</button>
            </div>
        </div>
    </div>
</div>
    `

    // This is to clean up the previously-generated modals
    $('#dynamicModal').remove()

    $('body').append(html)

    $('#dynamicModal').modal('show')

    $(`#btn-save-account-${username}`).on('click', function () {
        var form = $(`#form-edit-user-${username}`)

        for (let i = 0; i < form[0].length; i++) {
            if (!form[0][i].checkValidity()) {
                form.find(':submit').click()
                return
            }
        }

        // If we're here, that means the form is valid and we can submit it to WSs!
        sendEditAccountForm(form.serializeArray())

        setTimeout(function () {
            if (!$('#form-errors_edit').text()) {
                setTimeout(function () {
                    location.reload()
                }, 50)
            }
        }, 1500)
    })

    $(`#btn-remove-account-${username}`).on('click', function () {
        const form = $(`#form-edit-user-${username}`)
        if (confirm('Are you sure you want to remove the account?')) {
            sendRemoveAccountForm(form.serializeArray())
            lastRemovedAccount = `user\\:${username}`
        }
    })

    $(`#btn-node-acl-${username}`).on('click', function () {
        let permissions = ''
        try {
            permissions = JSON.parse($('#lsoc_permissions').val().replace(/[']/g, '"'))
        } catch (_) {
            console.info('Failed to read lsoc_permissions field. Using empty...')
        } finally {
            for (const node in permissions) {
                permissions[node].forEach(element => {
                    $(`#${node}\\:${element}`).prop('checked', 'checked')
                    $(`#${node}\\:${element}`).change()
                })
            }
        }
    })
}

$('#btn-submit-user').on('click', function () {
    var form = $('#form-user-add')

    for (let i = 0; i < form[0].length; i++) {
        if (!form[0][i].checkValidity()) {
            form.find(':submit').click()
            return
        }
    }

    sendNewAccountForm(form.serializeArray())
})

function sendEditAccountForm (data) {
    ws.send(JSON.stringify({
        type: 'account.edit',
        data: data
    }))
}

function sendRemoveAccountForm (data) {
    ws.send(JSON.stringify({
        type: 'account.remove',
        data: data
    }))
}

function sendNewAccountForm (data) {
    ws.send(JSON.stringify({
        type: 'account.register',
        data: data
    }))
}

(function ($) {
    $.fn.checktree = function () {
        $(document).on('change', "input[type='checkbox']", function (event) {
            var ide = event.currentTarget.id.split(':', 2)

            // If ide[1] is not undefined, the user clicked on an element(child of a node), else it was a node(parent).
            if (ide[1]) {
                var nodeID = ide[0]
                var elementAddress = ide[1]

                if (event.currentTarget.checked) {
                    if (nodeID in dict) {
                        if (!(dict[nodeID].includes(elementAddress))) {
                            dict[nodeID].push(elementAddress)
                        }
                    } else {
                        dict[nodeID] = [elementAddress]
                    }
                } else {
                    if (nodeID in dict) {
                        if (dict[nodeID].includes(elementAddress)) {
                            var index = dict[nodeID].indexOf(elementAddress)
                            dict[nodeID].splice(index, index + 1)
                            if (dict[nodeID].length === 0) {
                                delete dict[nodeID]
                            }
                        }
                    }
                }
            } else {
                var checkboxID = event.currentTarget.id

                if (event.currentTarget.checked) {
                    if (checkboxID === 'all_nodes') {
                        nodeElementList.forEach(node => {
                            dict[node['identifier']] = []

                            node['elements'].forEach(element => {
                                dict[node['identifier']].push(element['address'])
                            })
                        })
                    } else {
                        dict[checkboxID] = []
                        for (node in nodeElementList) {
                            if (checkboxID === nodeElementList[node].identifier) {
                                // If the parent node was checked, check all the children chkbxs
                                nodeElementList[node]['elements'].forEach(elem => {
                                    dict[checkboxID].push(elem['address'])
                                })
                            }
                        }
                    }
                } else {
                    if (checkboxID === 'all_nodes') {
                        dict = {}
                    } else {
                        delete dict[checkboxID]
                    }
                }
            }
            // console.log(dict)

            event.stopPropagation()
            var clkCheckbox = $(this)
            var chkState = clkCheckbox.is(':checked')
            var parentLI = clkCheckbox.closest('li')
            var parentULs = parentLI.parents('ul')
            parentLI.find(':checkbox').prop('checked', chkState)
            parentULs.each(function () {
                var parentUL = $(this)
                var parentState = (parentUL.find(':checkbox').length === parentUL.find(':checked').length)
                parentUL.siblings(':checkbox').prop('checked', parentState)
            })
        })
    }
}(jQuery))
