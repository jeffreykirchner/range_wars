/**
 * setup boxes for the current treatment
 */
setup_treatment : function setup_treatment(){
    let values = app.session.parameter_set.parameter_set_treatments[current_treatment].values.split(",");
    let parameter_set_players = app.session.parameter_set.parameter_set_players;
    let parameter_set_players_order = app.session.parameter_set.parameter_set_players_order;

    box_width = axis_width / values.length;

    let start_location_x = y_axis_margin;

    for(let i in values)
    {
        let box_json = {revenue_boxes: {}};
                        
        let box = new PIXI.Container();

        let outline = new PIXI.Graphics();

        let value = parseFloat(values[i]);
        let y = app.value_to_y(value);

        outline.rect(0,0, box_width, y);
        outline.stroke({color: "lightgray",
                        width: 2,
                        lineJoin: "round",
                        cap: "round"});

        box.x = start_location_x;
        box.y = origin_y - y;

        box_json.box = box;

        //add stacked revenues
        for(let p in parameter_set_players_order)
        {
            let parameter_set_player_id = parameter_set_players_order[p];
            let parameter_set_player = parameter_set_players[parameter_set_player_id];
            let revenue_box = new PIXI.Graphics();
            revenue_box.rect(0,20, box_width, 0)
            revenue_box.fill({color: parameter_set_player.hex_color});

            box.addChild(revenue_box);
            box_json.revenue_boxes[p] = revenue_box;
        }

        box.addChild(outline);

        pixi_boxes.push(box_json);

        pixi_container_main.addChild(box);
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