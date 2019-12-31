/* eslint-disable no-useless-escape */

(function ($) {
    'use strict' // Start of use strict

    // By setting the href attribute, we make it look better as a link/button
    $('#load-system_config').attr('href', '/staff/system_configuration')

// eslint-disable-next-line no-undef
})(jQuery) // End of use strict

// eslint-disable-next-line no-undef
$(function ($) {
    'use strict' // Start of use strict

    // Toggle the log-out confirmation modal
    $('#btn-logout').on('click', function () {
        $('#modalLogOut').modal('show')
    })
    $('#btn-logout-yes').on('click', function () {
        location.href = '/logout/?next=/'
    })

    if (window.location.href.includes('/staff/system_configuration')) {
        setActive('load-system_config')
    }

    // Removes the 'active' class from every element whose id starts with 'load' and adds the 'active' class to the element with the supplied 'id'.
    function setActive (buttonID) {
        $('[id^=load]').removeClass('active')
        $('#' + buttonID).toggleClass('active')
    }
})

var entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;'
}

// eslint-disable-next-line no-unused-vars
function escapeHtml (string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return entityMap[s]
    })
}
