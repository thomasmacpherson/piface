PIN_IN_X  = [6.0,   19.0,  31.0,  44.0,  56.0,  68.0,  80.0,  92.0 ];
PIN_IN_Y  = [186.0, 186.0, 186.0, 186.0, 186.0, 186.0, 186.0, 186.0];
PIN_OUT_X = [266.0, 254.0, 242.0, 230.0, 218.0, 206.0, 194.0, 181.0];
PIN_OUT_Y = [8.0,   8.0,   8.0,   8.0,   8.0,   8.0,   8.0,   8.0  ];
PIN_R     = 5;

var error_handler = function(jqXHR, text_status, error_thrown)
{
    alert(text_status + ": " + error_thrown + "\n" + jqXHR.responseText);
    window.setInterval(0);
};

var send_ajax = function(datatosend, success_func)
{
    $.ajax({url: '/piface/ajax',
        data: datatosend,
        success: success_func,
        error: error_handler});
};

var write_completed = function(data, output_status, jqXHR)
{
};

var output_checkbox_clicked = function(the_event)
{
    // generate binary
    var output_bitp = 0;
    for (var i=8; i >= 1; i--) // first output is on rhs
    {
        output_bitp = output_bitp << 1;
        if ($("#pifaceoutputcheckbox"+i).prop('checked'))
            output_bitp ^= 1;
    }

    send_ajax("write_output="+output_bitp, write_completed)
};

var draw_circle = function(context, x, y, r, colour)
{
    colour = typeof colour !== 'undefined' ? colour : "#8ed6ff";
    context.beginPath();
    context.arc(x, y, r, 0, 2 * Math.PI, false);
    context.fillStyle = colour;
    context.fill();
    context.lineWidth = 1;
    context.strokeStyle = "black";
    context.stroke();
};

var set_in_pin = function(context, pin_number, set_pin)
{
    if (set_pin)
        draw_circle(context, PIN_IN_X[pin_number], PIN_IN_Y[pin_number], PIN_R);
};

var set_out_pin = function(context, pin_number, set_pin)
{
    if (set_pin)
        draw_circle(context, PIN_OUT_X[pin_number], PIN_OUT_Y[pin_number], PIN_R);
};

var update_piface = function(data, output_status, jqXHR)
{
    send_ajax("read_input&read_output", function(data, output_status, jqXHR)
    {
        var data = eval("("+data+")"); // convert text to a json object

        // once we have the I/O stuff, then draw everything
        var canvas  = document.getElementById("pifacecanvas");
        var context = canvas.getContext("2d");

        // reset the canvas
        canvas.width = canvas.width;

        // draw the pins
        for (var i = 0; i <= 7; i++)
        {
            set_in_pin(context,  i, (data.input_bitp  >> i) & 1);
            set_out_pin(context, i, (data.output_bitp >> i) & 1);
        }
    }); // ajax callback
};

/* sets up the page */
var setup = function()
{
    // set some event listeners
    for (var i=1; i <= 8; i++)
        $("#pifaceoutputcheckbox"+i).click(output_checkbox_clicked);

    update_piface(); // update now
    // update the board every second
    window.setInterval(update_piface, 1000);
};

$(document).ready(setup);
