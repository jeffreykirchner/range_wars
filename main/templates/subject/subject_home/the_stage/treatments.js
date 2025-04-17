/**
 * setup boxes for the current treatment
 */
setup_treatment : function setup_treatment(){
    if(!app.current_treatment) return;

    let treatment = app.session.parameter_set.parameter_set_treatments[app.current_treatment];
    let values = treatment.values.split(",");
    let parameter_set_players = app.session.parameter_set.parameter_set_players;
    let parameter_set_players_order = app.session.parameter_set.parameter_set_players_order;

    // box_width = (axis_width * (treatment.range_width/treatment.scale_width))  / values.length;

    //destory pixi boxes
    for(let i=0;i<pixi_boxes.length;i++)
    {
        let box = pixi_boxes[i].box;
        box.destroy();
    }
    pixi_boxes = [];

    let start_location_x = y_axis_margin;

    for(let i in values)
    {
        let box_json = {revenue_boxes: {},
                        height: 0,                        
                        };
                        
        let box = new PIXI.Container();

        let outline = new PIXI.Graphics();

        let value = parseFloat(values[i]);
        let y = app.value_to_y(value);

        outline.rect(0,0, box_width, y);
        outline.stroke({color: "lightgray",
                        width: 1,
                        lineJoin: "round",
                        alignment: 0.5,
                        cap: "round"});
        outline.zIndex = 999;

        box.x = start_location_x;
        box.y = origin_y - y;

        box_json.box = box;
        box_json.height = y;

        box.addChild(outline);

        pixi_boxes.push(box_json);

        pixi_container_main.addChild(box);
        start_location_x += box_width;
    }
},

/**
 * update the boxes for the current treatment
 */
update_treatment : function update_treatment(){
    if(!app.current_treatment) return;
    
    let values = app.session.parameter_set.parameter_set_treatments[app.current_treatment].values.split(",");
    let parameter_set_players = app.session.parameter_set.parameter_set_players;
    let parameter_set_players_order = app.session.parameter_set.parameter_set_players_order;
    let world_state = app.session.world_state;
    let current_group_memebers = app.session.started ? world_state["groups"][app.current_group] : [];
    let session_players = world_state["session_players"];

    //reset profit highlights
    for(let p in current_group_memebers)
    {
        pixi_profit_hightlights[current_group_memebers[p]] = [];        
        pixi_cost_hightlights[current_group_memebers[p]] = []; // reset cost highlights for current group members
    }
    pixi_waste_highlights = [];

    for(let i=0;i<pixi_boxes.length;i++)
    {   
        let value = values[i];
        let box = pixi_boxes[i].box;

        //set box height to zero
        // for(let b in pixi_boxes[i].revenue_boxes)
        // {
        //     pixi_boxes[i].revenue_boxes[b].height = 0;
        // }

        //find number if group members in this box
        let group_members_in_box = [];
        let counter = 0;
        for(let p in current_group_memebers)
        {
            let session_player = session_players[current_group_memebers[p]];
            if(session_player.range_start <= i && session_player.range_end >= i)
            {
                group_members_in_box.push(p);
            }
        }

        let total_height = pixi_boxes[i].height;
        let height_per_player = total_height / group_members_in_box.length;
        let start_y = total_height-height_per_player;

        //destory old boxes
        for(let p in pixi_boxes[i].revenue_boxes)
        {
            pixi_boxes[i].revenue_boxes[p].destroy();           
        }

        for(let p in group_members_in_box)
        {
            let session_player_id = current_group_memebers[group_members_in_box[p]];
            let session_player = app.session.world_state.session_players[session_player_id];
            let parameter_set_player = parameter_set_players[session_player.parameter_set_player_id];

            let revenue_box = new PIXI.Container();

            let revenue_box_fill = new PIXI.Graphics();
            revenue_box_fill.rect(0, 0, box_width, height_per_player)
            revenue_box_fill.fill({color: parameter_set_player.hex_color});

            revenue_box.addChild(revenue_box_fill);

            //cost box
            let cost_y = app.value_to_y(session_player.cost);
            let cost_y1 = height_per_player-cost_y
            let cost_height1 = cost_y;
    
            let cost_box = new PIXI.Graphics();  
            cost_box.rect(0, cost_y1, box_width, cost_height1);
            
            // if(app.session.parameter_set.show_waste)
            // {            
            //     cost_box.fill({color: "white", alpha: 0.5});
            //     revenue_box.addChild(cost_box);
            // }
            // else
            // {
                //fill with texture 2
            let texture_scale = box_width / app.pixi_textures['pattern_2_tex'].width;
            const matrix = new PIXI.Matrix().scale(texture_scale,texture_scale).translate(0, cost_y1);
            cost_box.fill({texture: app.pixi_textures['pattern_2_tex'],
                            matrix:matrix});
            revenue_box.addChild(cost_box);
            // }

            //draw cost loss for local player
            if(app.is_subject && session_player_id == app.session_player.id)
            {  
                //loss
                if(height_per_player-cost_y < 0)
                {
                    //loss pattern fill
                    // let cost_y2 = height_per_player-cost_y;

                    // let cost_box2 = new PIXI.Graphics();
                    // cost_box2.rect(0, cost_y2, box_width, cost_y1 - cost_y2);

                    // let texture_scale = app.pixi_textures['pattern_1_tex'].width / box_width;
                    // const matrix = new PIXI.Matrix().scale(texture_scale, texture_scale).translate(0, cost_y2);

                    // cost_box2.fill({texture: app.pixi_textures['pattern_1_tex'],
                    //                 matrix:matrix});
                    
                    // revenue_box.addChild(cost_box2);

                    //loss text
                    let loss_text = new PIXI.Text({text:"!",
                                                   style: {fontFamily : 'Arial', 
                                                           fontSize: 18, 
                                                           fill : 'black', 
                                                              fontWeight: 'bold',
                                                           align : 'center'}});
                    loss_text.x = box_width/2;
                    loss_text.y = height_per_player;
                    loss_text.anchor.set(0.5,0);
                    revenue_box.addChild(loss_text);
                }

                // Calculate waste for this player in this box
                // if (group_members_in_box.length > 1 && app.session.parameter_set.show_waste) {
                //     // let waste_y = app.value_to_y(session_player.cost * (group_members_in_box.length - 1) / group_members_in_box.length);
                //     let waste_y = app.value_to_y(session_player.cost * (group_members_in_box.length - 1));
                //     // session_player.cost * (group_members_in_box.length - 1) / group_members_in_box.length

                //     let waste_box = new PIXI.Graphics();                    
                //     waste_box.rect(0, height_per_player - waste_y, box_width, waste_y);

                //     let texture_scale = box_width/app.pixi_textures['pattern_2_tex'].width;
                //     const matrix = new PIXI.Matrix().scale(texture_scale,texture_scale).translate(0, height_per_player - waste_y);

                //     waste_box.fill({texture: app.pixi_textures['pattern_2_tex'],                                    
                //                     matrix: matrix,});

                //     revenue_box.addChild(waste_box);
                // }

                revenue_box.zIndex = 998;
            }

            //add profit highlights            
            if(revenue_box.y < cost_y1)
            {
                let profit_box_highlight = new PIXI.Graphics();
                // let profit_y_highlight = app.value_to_y(session_player.profit);
                profit_box_highlight.rect(revenue_box.x, revenue_box.y, revenue_box.width, cost_y1);
                profit_box_highlight.stroke({color: "yellow",
                                width: 3,
                                lineJoin: "round",
                                alignment: 1,
                                cap: "round"});
                profit_box_highlight.visible = false;
                revenue_box.addChild(profit_box_highlight);
                pixi_profit_hightlights[session_player_id].push(profit_box_highlight);
            }

            //add cost highlights
            let cost_box_highlight = new PIXI.Graphics();
            cost_box_highlight.rect(revenue_box.x, cost_y1, revenue_box.width, cost_height1);
            cost_box_highlight.stroke({color: "yellow",
                            width: 3,
                            lineJoin: "round",
                            alignment: 1,
                            cap: "round"});
            cost_box_highlight.visible = false;
            revenue_box.addChild(cost_box_highlight);
            pixi_cost_hightlights[session_player_id].push(cost_box_highlight);
            
            revenue_box.x = 0;
            revenue_box.y = start_y;

            pixi_boxes[i].revenue_boxes[p] = revenue_box;
            box.addChild(revenue_box);

            //add waste highlight
            if(group_members_in_box.length > 1)
            {
                let waste_highlight = new PIXI.Graphics();
                waste_highlight.rect(revenue_box.x, cost_y1, revenue_box.width, cost_height1 * (group_members_in_box.length - 1)/ group_members_in_box.length);
                waste_highlight.stroke({color: "yellow",
                                width: 3,
                                lineJoin: "round",
                                alignment: 1,
                                cap: "round"});
                waste_highlight.visible = false;
                revenue_box.addChild(waste_highlight);
                pixi_waste_highlights.push(waste_highlight);
            }

            start_y -= height_per_player;
        }
    }
},

/**
 * convert a value to a y coordinate
 */
value_to_y : function value_to_y(value){

    let unit_rate = axis_height / app.session.parameter_set.parameter_set_treatments[app.current_treatment].scale_height;

    return value * unit_rate;

},

/**
 * convert range selection to x coordinate
 */
range_to_x : function range_to_x(range)
{
    return (box_width * range) + y_axis_margin;
},

/**
 * convert x value to range
 */
x_to_range : function x_to_range(x)
{
    let values_count = app.session.parameter_set.parameter_set_treatments[app.current_treatment].values.split(',').length;
    if(x <= y_axis_margin) return 0;
    if(x >= (axis_width + y_axis_margin)) return values_count - 1;

    let r = Math.floor((x - y_axis_margin) / box_width);

    if(r > values_count-1)
    {
        r = values_count - 1;
    }

    return r;
},