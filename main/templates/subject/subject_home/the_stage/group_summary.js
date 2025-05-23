/**
 * setup the group summary graph
 */
setup_group_summary : function setup_group_summary(){
    if(!app.session.started) return;

    if(pixi_group_summary) pixi_group_summary.destroy();

    if(app.session.parameter_set.summary_type == "Full")
    {
        app.setup_group_summary_full();
    }
    else
    {
        app.setup_group_summary_partial();
    }
},

/**
 * draw full group summary graph
 */
setup_group_summary_full : function setup_group_summary_full(){
    
    let parameter_set_players = app.session.parameter_set.parameter_set_players;

    pixi_group_summary = new PIXI.Container();
    let scaler = 1;
    let margin = 10;
    let small_margin = 5;

    let world_state = app.session.world_state;
    let current_group_memebers = world_state.groups[app.current_group];

    pixi_profit_bars = {};

    //border
    let box = new PIXI.Graphics();

    let rect_height = 50 + 40 * current_group_memebers.length;

    if(app.session.parameter_set.show_waste)
    {
        rect_height += 30;
    }   

    box.roundRect(0, 0, axis_width * 0.25, rect_height, 10);
    box.stroke({color: "black", width: 1});
    pixi_group_summary.addChild(box);

    //caption
    let text_style = {fontSize: 15, fill : 0x000000, align : 'center', fontWeight: 'bold'};
    let summary_label = new PIXI.Text({text:"Summary", style:text_style});
    summary_label.pivot.set(summary_label.width/2, 0);
    summary_label.position.set(box.width/2, 2);
    pixi_group_summary.addChild(summary_label);

    //sub captions
    let text_style_sub = {fontSize: 15, fill : 0x000000, align : 'center'};
    let text_cost = new PIXI.Text({text:"⇐ Cost", style:text_style_sub});

    text_cost.pivot.set(text_cost.width, 0);
    text_cost.position.set(0, summary_label.y + summary_label.height + margin);
    pixi_group_summary.addChild(text_cost);

    let text_profit = new PIXI.Text({text:"Profit ⇒", style:text_style_sub});
    text_profit.pivot.set(0, 0);
    text_profit.position.set(box.width, summary_label.y + summary_label.height + margin);
    pixi_group_summary.addChild(text_profit);

    //bars   
    let start_y = small_margin + text_profit.y + text_profit.height;
    let waste_margin = 0;
    if(app.session.parameter_set.show_waste)
    {
        waste_margin = 30;
    }

    let bar_height = (box.height-text_profit.height-text_profit.y-margin-small_margin-margin*(current_group_memebers.length-1)-waste_margin) / current_group_memebers.length;
    let max_cost = 0;
    let max_profit = 0;
    let center_x = 0;
    
    //find scaler
    for(let i in current_group_memebers)
    {
        let player = world_state.session_players[current_group_memebers[i]];
        max_cost = Math.max(max_cost, player.total_cost);
        max_profit = Math.max(max_profit, player.total_profit);
    }

    if(max_cost + max_profit > 0)
    {
        scaler = (box.width-margin*2) / (max_cost + max_profit);
        center_x = max_cost * scaler + margin;
    }
    else
    {
        center_x = box.width / 2;
    }

    //check for minimum label clearance
    if(center_x > box.width - text_profit.width - margin)
    {
        scaler = (box.width - text_profit.width - margin) / center_x * scaler;
        center_x = max_cost * scaler + margin;
    }
    else if(text_cost.width + margin>center_x)
    {
        scaler = (box.width-text_cost.width-margin*2) / (max_cost + max_profit);
        center_x = max_cost * scaler + text_cost.width + margin;
    }

    //move sub captions
    text_cost.x = center_x - small_margin;
    text_profit.x = center_x + small_margin;

    //center line
    let center_line = new PIXI.Graphics();
    center_line.moveTo(center_x, start_y+3);
    center_line.lineTo(center_x, box.height-margin-6-waste_margin);
    center_line.stroke({color: "black", width: 1});
    center_line.zIndex = 999;

    pixi_group_summary.addChild(center_line);

    //draw bars
    for(let i=current_group_memebers.length-1;i>=0;i--)
    {
        let player_id = current_group_memebers[i];
        let player = world_state.session_players[player_id];      
        let parameter_set_player = parameter_set_players[player.parameter_set_player_id];

        //profit bar
        let bar = new PIXI.Graphics();
        let bar_width = (player.total_profit) * scaler;
        let bar_color = parameter_set_player.hex_color;

        bar.roundRect(center_x,
                 start_y, 
                 bar_width, 
                 bar_height,
                 6);

        bar.fill({color: bar_color});
        bar.stroke({color: "lightgrey", width: 1});

        pixi_profit_bars[player_id] = {x:center_x, y:start_y, width:bar_width, height:bar_height};

        //cost bar
        let bar_cost = new PIXI.Graphics();
        bar_width = (player.total_cost) * scaler;
        bar_color = parameter_set_player.hex_color;

        bar_cost.roundRect(center_x-bar_width,
                    start_y, 
                    bar_width, 
                    bar_height,
                    6);

        bar_cost.fill({color: bar_color,alpha:0.5});
        bar_cost.stroke({color: "lightgrey", width: 1});

        pixi_cost_bars[player_id] = {x:center_x-bar_width, y:start_y, width:bar_width, height:bar_height};

        pixi_group_summary.addChild(bar_cost);
        pixi_group_summary.addChild(bar);

        //text cost
        let text_cost = new PIXI.Text({text:player.total_cost + "¢", style:text_style_sub});
        text_cost.pivot.set(text_cost.width, text_cost.height/2);
        text_cost.position.set(center_x - small_margin, start_y+bar.height/2);
        pixi_group_summary.addChild(text_cost);

        //text profit
        let text_profit = new PIXI.Text({text:player.total_profit + "¢", style:text_style_sub});
        text_profit.pivot.set(0, text_profit.height/2);
        text_profit.position.set(center_x + small_margin, start_y+bar.height/2);
        pixi_group_summary.addChild(text_profit);
        
        start_y += bar_height + margin;
    }

    //waste text
    if(app.session.parameter_set.show_waste)
    {
        let total_waste = 0;
        for(let i=current_group_memebers.length-1;i>=0;i--)
        {
            let player_id = current_group_memebers[i];
            let player = world_state.session_players[player_id];
            total_waste += parseFloat(player.total_waste);
        }
        let waste_text = new PIXI.Text({text:"Total Waste: " + total_waste.toFixed(3) + "¢", 
                                        style:text_style_sub});
       
        waste_text.position.set(box.width/2, start_y);
        waste_text.anchor.set(0.5, 0);
        pixi_group_summary.addChild(waste_text);

        pixi_waste_bar = {x:waste_text.x-waste_text.width/2, 
                          y:waste_text.y, 
                          width:waste_text.width, 
                          height:waste_text.height};
    }

    //help box button
    let help_box_button = new PIXI.Sprite(PIXI.Assets.get('question_mark_text'));
    help_box_button.eventMode = 'static'; // PixiJS v8: make sprite interactive/clickable
    help_box_button.cursor = 'pointer';   // Show pointer cursor on hover
    help_box_button.position.set(box.width-help_box_button.width - 7, 7);
    help_box_button.on('pointerdown', () => {
        app.send_load_help_doc_subject('Group Summary');
    });

    pixi_group_summary.addChild(help_box_button);

    pixi_group_summary.position.set(axis_width * 0.71 - pixi_group_summary.width/2, other_margin+6);
    
    pixi_container_main.addChild(pixi_group_summary);
},

/**
 * draw partial summary graph
 */
setup_group_summary_partial : function setup_group_summary_partial(){
    let parameter_set_players = app.session.parameter_set.parameter_set_players;

    pixi_group_summary = new PIXI.Container();
    let scaler = 1;
    let margin = 10;
    let small_margin = 5;

    let world_state = app.session.world_state;
    let current_group_memebers = world_state.groups[app.current_group];

    pixi_profit_bars = {};

    //border
    let box = new PIXI.Graphics();

    let rect_height = 50 + 40;

    if(app.session.parameter_set.show_waste)
    {
        rect_height += 30;
    }   

    box.roundRect(0, 0, axis_width * 0.25, rect_height, 10);
    box.stroke({color: "black", width: 1});
    pixi_group_summary.addChild(box);

    //caption
    let text_style = {fontSize: 15, fill : 0x000000, align : 'center', fontWeight: 'bold'};
    let summary_label = new PIXI.Text({text:"Summary", style:text_style});
    summary_label.pivot.set(summary_label.width/2, 0);
    summary_label.position.set(box.width/2, 2);
    pixi_group_summary.addChild(summary_label);

    //sub captions
    let text_style_sub = {fontSize: 15, fill : 0x000000, align : 'center'};
    let text_cost_label = new PIXI.Text({text:"⇐ Cost", style:text_style_sub});

    text_cost_label.pivot.set(text_cost_label.width, 0);
    text_cost_label.position.set(0, summary_label.y + summary_label.height + margin);
    pixi_group_summary.addChild(text_cost_label);

    let text_profit_label = new PIXI.Text({text:"Profit ⇒", style:text_style_sub});
    text_profit_label.pivot.set(0, 0);
    text_profit_label.position.set(box.width, summary_label.y + summary_label.height + margin);
    pixi_group_summary.addChild(text_profit_label);

    //bars   
    let start_y = small_margin + text_profit_label.y + text_profit_label.height;
    let waste_margin = 0;
    if(app.session.parameter_set.show_waste)
    {
        waste_margin = 30;
    }

    let bar_height = 35;
    let max_cost = 0;
    let max_profit = 0;
    let center_x = 0;
    
    //find scaler 
    let player_id = app.session_player.id;
    let player = world_state.session_players[player_id];
    max_cost = Math.max(max_cost, player.total_cost);
    max_profit = Math.max(max_profit, player.total_profit);
    
    if(max_cost + max_profit > 0)
    {
        scaler = (box.width-margin*2) / (max_cost + max_profit);
        center_x = max_cost * scaler + margin;
    }
    else
    {
        center_x = box.width / 2;
    }

    //check for minimum label clearance
    if(center_x > box.width - text_profit_label.width - margin)
    {
        scaler = (box.width - text_profit_label.width - margin) / center_x * scaler;
        center_x = max_cost * scaler + margin;
    }
    else if(text_cost_label.width + margin>center_x)
    {
        scaler = (box.width-text_cost.width-margin*2) / (max_cost + max_profit);
        center_x = max_cost * scaler + text_cost.width + margin;
    }

    //move sub captions
    text_cost_label.x = center_x - small_margin;
    text_profit_label.x = center_x + small_margin;

    //center line
    let center_line = new PIXI.Graphics();
    center_line.moveTo(center_x, start_y+3);
    center_line.lineTo(center_x, box.height-margin-waste_margin);
    center_line.stroke({color: "black", width: 1});
    center_line.zIndex = 999;

    pixi_group_summary.addChild(center_line);

    //draw bars
    let parameter_set_player = parameter_set_players[player.parameter_set_player_id];

    //profit bar
    let bar = new PIXI.Graphics();
    let bar_width = (player.total_profit) * scaler;
    let bar_color = parameter_set_player.hex_color;

    bar.roundRect(center_x,
                start_y, 
                bar_width, 
                bar_height,
                6);

    bar.fill({color: bar_color});
    bar.stroke({color: "lightgrey", width: 1});

    pixi_profit_bars[player_id] = {x:center_x, y:start_y, width:bar_width, height:bar_height};

    //cost bar
    let bar_cost = new PIXI.Graphics();
    bar_width = (player.total_cost) * scaler;
    bar_color = parameter_set_player.hex_color;

    bar_cost.roundRect(center_x-bar_width,
                start_y, 
                bar_width, 
                bar_height,
                6);

    bar_cost.fill({color: bar_color,alpha:0.5});
    bar_cost.stroke({color: "lightgrey", width: 1});

    pixi_cost_bars[player_id] = {x:center_x-bar_width, y:start_y, width:bar_width, height:bar_height};

    pixi_group_summary.addChild(bar_cost);
    pixi_group_summary.addChild(bar);

    //text cost
    let text_cost = new PIXI.Text({text:player.total_cost + "¢", style:text_style_sub});
    text_cost.pivot.set(text_cost.width, text_cost.height/2);
    text_cost.position.set(center_x - small_margin, start_y+bar.height/2);
    pixi_group_summary.addChild(text_cost);

    //text profit
    let text_profit = new PIXI.Text({text:player.total_profit + "¢", style:text_style_sub});
    text_profit.pivot.set(0, text_profit.height/2);
    text_profit.position.set(center_x + small_margin, start_y+bar.height/2);
    pixi_group_summary.addChild(text_profit);
    
    start_y += bar_height + margin;
    
    //waste text
    if(app.session.parameter_set.show_waste)
    {

        let total_waste = parseFloat(player.total_waste);
        
        let waste_text = new PIXI.Text({text:"Your Waste: " + total_waste.toFixed(3) + "¢", 
                                        style:text_style_sub});
       
        waste_text.position.set(box.width/2, start_y);
        waste_text.anchor.set(0.5, 0);
        pixi_group_summary.addChild(waste_text);

        pixi_waste_bar = {x:waste_text.x-waste_text.width/2, 
                          y:waste_text.y, 
                          width:waste_text.width, 
                          height:waste_text.height};
    }

    //help box button
    let help_box_button = new PIXI.Sprite(PIXI.Assets.get('question_mark_text'));
    help_box_button.eventMode = 'static'; // PixiJS v8: make sprite interactive/clickable
    help_box_button.cursor = 'pointer';   // Show pointer cursor on hover
    help_box_button.position.set(box.width-help_box_button.width - 7, 7);
    help_box_button.on('pointerdown', () => {
        app.send_load_help_doc_subject('Group Summary');
    });

    pixi_group_summary.addChild(help_box_button);

    pixi_group_summary.position.set(axis_width * 0.71 - pixi_group_summary.width/2, other_margin+6);
    
    pixi_container_main.addChild(pixi_group_summary);
},
