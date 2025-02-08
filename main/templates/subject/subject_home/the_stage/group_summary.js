/**
 * setup the group summary graph
 */
setup_group_summary : function setup_group_summary(){

    if(pixi_group_summary) pixi_group_summary.destroy();

    let parameter_set_players = app.session.parameter_set.parameter_set_players;

    pixi_group_summary = new PIXI.Container();
    let scaler = 1;
    let margin = 10;
    let small_margin = 5;

    let world_state = app.session.world_state;
    let current_group_memebers = world_state["groups"][current_group];

    //border
    let box = new PIXI.Graphics();
    box.roundRect(0, 0, axis_width * 0.25, axis_height*0.3, 10);
    box.stroke({color: "black", width: 1});
    pixi_group_summary.addChild(box);

    //caption
    let text_style = {fontSize: 15, fill : 0x000000, align : 'center', fontWeight: 'bold'};
    let summary_label = new PIXI.Text({text:"Group Summary", style:text_style});
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
    let bar_height = (box.height-text_profit.height-text_profit.y-margin-small_margin-margin*(current_group_memebers.length-1)) / current_group_memebers.length;
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

    scaler = (box.width-margin*2) / (max_cost + max_profit);
    center_x = max_cost * scaler + margin;

    //move sub captions
    text_cost.x = center_x - small_margin;
    text_profit.x = center_x + small_margin;

    //center line
    let center_line = new PIXI.Graphics();
    center_line.moveTo(center_x, start_y);
    center_line.lineTo(center_x, box.height-margin);
    center_line.stroke({color: "black", width: 1});
    center_line.zIndex = 999;

    pixi_group_summary.addChild(center_line);

    //draw bars
    for(let i in current_group_memebers)
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

        pixi_group_summary.addChild(bar);

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
        pixi_group_summary.addChild(bar_cost);

        //text cost
        let text_cost = new PIXI.Text({text:player.total_cost, style:text_style_sub});
        text_cost.pivot.set(text_cost.width, text_cost.height/2);
        text_cost.position.set(center_x - small_margin, start_y+bar.height/2);
        pixi_group_summary.addChild(text_cost);

        //text profit
        let text_profit = new PIXI.Text({text:player.total_profit, style:text_style_sub});
        text_profit.pivot.set(0, text_profit.height/2);
        text_profit.position.set(center_x + small_margin, start_y+bar.height/2);
        pixi_group_summary.addChild(text_profit);
        
        start_y += bar_height + margin;
    }

    pixi_group_summary.position.set(axis_width * 0.68 - pixi_group_summary.width/2, other_margin+5);
    
    pixi_container_main.addChild(pixi_group_summary);
},