/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */

function notification (title = '', message, type = 'info', progressBar = false, delay = 5, refreshPage = false) {
    $.notify({
        title: `<strong>${escapeHtml(title)}</strong>`,
        message: escapeHtml(message)
    }, {
        delay: delay * 1000,
        showProgressbar: progressBar,
        animate: {
            enter: 'animated fadeInDown',
            exit: 'animated fadeOutUp'
        },
        type: type,
        z_index: 10031,
        placement: {
            from: 'bottom',
            align: 'center'
        },
        // eslint-disable-next-line no-self-assign
        onClosed: function () { if (refreshPage) { location.href = location.href } }
    })
}
