setup_axis : function setup_axis(){


    if(!app.current_treatment) return;

    let treatment = app.session.parameter_set.parameter_set_treatments[app.current_treatment];
    let values = treatment.values.split(",");

    //add white background
    let background = new PIXI.Graphics();    
    background.rect(0, 0, app.canvas_width, app.canvas_height);
    background.fill(0xFFFFFF);
    pixi_container_main.addChild(background);

    if(app.is_subject)
    {
        background.eventMode = 'static';
        background.on('pointerup', app.pixi_container_main_pointerup);    
        background.on('pointerout', app.pixi_container_main_pointerup);
        background.on('pointerdown', app.pixi_container_main_pointerdown);
        background.on('pointermove', app.pixi_container_main_pointermove);
    }

    
    //setup sizes
    axis_width = app.canvas_width - y_axis_margin - right_margin;
    axis_height = app.canvas_height - x_axis_margin - other_margin;
    box_width = (axis_width * (treatment.range_width/treatment.scale_width))  / values.length;

    //setup origin
    origin_x = y_axis_margin;
    origin_y = app.canvas_height - x_axis_margin;

    //axis
    let axis = new PIXI.Graphics();

    axis.moveTo(origin_x, other_margin);
    axis.lineTo(origin_x, origin_y);
    axis.lineTo(axis_width + origin_x, origin_y);
    
    axis.stroke({color: "black", 
                 width: 4, 
                 lineJoin: "round", 
                 cap: "round"});
     
    //add to stage
    axis.zIndex = 1;
    pixi_container_main.addChild(axis);
    pixi_axis = axis;

    //axis labels
    // let x_label = new PIXI.Text({text:"Range",style:axis_style});
    // x_label.position.set(y_axis_margin + axis_width/2, app.canvas_height - 23);
    // pixi_container_main.addChild(x_label);

    let y_label = new PIXI.Text({text:"Resource Value (¢)",style:axis_style});
    y_label.position.set(1, other_margin + axis_height/2);
    y_label.rotation = -Math.PI/2;
    pixi_container_main.addChild(y_label);

    //y axis ticks
    let tick_length = 5;

    for(let i=0; i<=treatment.scale_height_ticks; i++)
    {
        let y_value = treatment.scale_height * i / treatment.scale_height_ticks;
        let tick = new PIXI.Graphics();
        let y = app.value_to_y(y_value);

        tick.moveTo(y_axis_margin, origin_y-y);
        tick.lineTo(y_axis_margin-tick_length, origin_y-y);
        tick.stroke({color: "black", 
                     width: 2, });

        pixi_container_main.addChild(tick);
        
        let tick_label = new PIXI.Text({text:y_value.toFixed(2),style:axis_style});
        tick_label.anchor.set(1, 0.5);
        tick_label.position.set(y_axis_margin-tick_length-2, origin_y-y);
        pixi_container_main.addChild(tick_label);
    }

    //x axis ticks
    let tick_length_x = 5;

    for(let i=1; i<=values.length; i++)
    {
        let tick = new PIXI.Graphics();
        let x = app.range_to_x(i);

        tick.moveTo(x, origin_y);
        tick.lineTo(x, origin_y+tick_length_x);
        tick.stroke({color: "black", 
                     width: 2, });

        pixi_container_main.addChild(tick);

        if(i % 10 == 0)
        {
            let tick_label = new PIXI.Text({text:i.toString(),
                                            style:{fontFamily: 'Arial',
                                                fontSize: 12,
                                                fill: {color:'black'},
                                                align: 'center'}});
            tick_label.anchor.set(0.5, 0);
            tick_label.position.set(x, origin_y+tick_length_x);
            pixi_container_main.addChild(tick_label);
        }
    }

},