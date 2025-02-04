/**
 * setup boxes for the current treatment
 */
setup_treatment : function setup_treatment(){
    let values = app.session.parameter_set.parameter_set_treatments[current_treatment].values.split(",");

    box_width = axis_width / values.length;

    let start_location_x = y_axis_margin;

    for(let i in values)
    {
        let box = new PIXI.Graphics();
        let value = parseFloat(values[i]);
        let y = app.value_to_y(value);

        box.rect(start_location_x, origin_y-y, box_width, y);
        box.stroke({color: "lightgray",
                    width: 2,
                    lineJoin: "round",
                    cap: "round"});

        pixi_container_main.addChild(box);
        pixi_boxes.push(box);

        start_location_x += box_width;
    }
},

/**
 * convert a value to a y coordinate
 */
value_to_y : function value_to_y(value){

    let unit_rate = axis_height / app.session.parameter_set.parameter_set_treatments[current_treatment].range_height;

    return value * unit_rate;

},