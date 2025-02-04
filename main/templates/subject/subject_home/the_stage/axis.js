setup_axis : function setup_axis(){
    let treatment = app.session.parameter_set.parameter_set_treatments[current_treatment];

    //setup sizes
    axis_width = app.canvas_width - y_axis_margin - other_margin;
    axis_height = app.canvas_height - x_axis_margin - other_margin;

    //setup origin
    origin_x = y_axis_margin;
    origin_y = app.canvas_height - x_axis_margin;

    //axis
    let axis = new PIXI.Graphics();

    axis.moveTo(origin_x, other_margin);
    axis.lineTo(origin_x, origin_y);
    axis.lineTo(app.canvas_width - other_margin, origin_y);
    
    axis.stroke({color: "black", 
                 width: 4, 
                 lineJoin: "round", 
                 cap: "round"});
     
    //add to stage
    axis.zIndex = 1;
    pixi_container_main.addChild(axis);
    pixi_axis = axis;

    //axis labels
    let x_label = new PIXI.Text({text:"Range",style:axis_style});
    x_label.position.set(y_axis_margin + axis_width/2, app.canvas_height - 23);
    pixi_container_main.addChild(x_label);

    let y_label = new PIXI.Text({text:"Value",style:axis_style});
    y_label.position.set(3, other_margin + axis_height/2);
    y_label.rotation = -Math.PI/2;
    pixi_container_main.addChild(y_label);

    //y axis ticks
    let tick_length = 5;

    for(let i=0; i<=treatment.range_height_ticks; i++)
    {
        let tick = new PIXI.Graphics();
        let y = app.value_to_y(i);

        tick.moveTo(y_axis_margin, origin_y-y);
        tick.lineTo(y_axis_margin-tick_length, origin_y-y);
        tick.stroke({color: "black", 
                     width: 2, });

        pixi_container_main.addChild(tick);

        let tick_label = new PIXI.Text({text:i.toString(),style:axis_style});
        tick_label.anchor.set(1, 0.5);
        tick_label.position.set(y_axis_margin-tick_length-2, origin_y-y);
        pixi_container_main.addChild(tick_label);
    }

},