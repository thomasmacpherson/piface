var send_ajax = function(datatosend, success_func)
{
    $.ajax({url: '/piface/ajax', data: datatosend, success: success_func});
};

var write_completed = function(data, output_status, jqXHR)
{
    if (output_status != 'success')
        alert(data);
};

var output_checkbox_clicked = function(the_event)
{
    // generate binary
    var output_bitp = 0;
    for (var i=8; i >= 1; i--) // first output is on rhs
    {
        output_bitp = output_bitp << 1;
        if ($("#piface-output-checkbox"+i).prop('checked'))
            output_bitp ^= 1;
    }

    send_ajax("write_output="+output_bitp, write_completed)
};

var setup = function()
{
    for (var i=1; i <= 8; i++)
        $("#piface-output-checkbox"+i).click(output_checkbox_clicked);
}

$(document).ready(setup);
