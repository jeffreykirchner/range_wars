/**
 * send request to load session events
 */
send_load_session_events()
{
    app.working = true;
    app.send_message("load_session_events", {});  
},

/**
 * take load session events
 */
take_load_session_events(message_data)
{
    if(message_data.value == "fail")
    {
        
    }
    else
    {
        app.session_events = message_data.session_events;

        app.replay_current_period = 1;

        app.replay_load_world_state();
    }
},

/**
 * load world state for replay
 */
replay_load_world_state: function replay_load_world_state()
{
    let events = app.session_events[app.replay_current_period];

    for(let i in events)
    {
        if(events[i].type == "world_state")
        { 
            app.session.world_state = JSON.parse(JSON.stringify(events[i].data));           
            app.session.world_state["current_experiment_phase"] = "Done";

            app.current_treatment = app.get_current_treatment().id;
            app.current_group = 1;

            app.do_reload();  

            break;
        }
    }
},

/**
 * update the replay mode
 */
update_replay_mode: function update_replay_mode(new_replay_mode)
{
    app.replay_mode = new_replay_mode;

    if(app.replay_mode == "playing")
    {
        app.replay_mode_play();
    }
},

/**
 * replay mode play
 */
replay_mode_play: function replay_mode_play()
{
    if(app.replay_mode == "paused") return;

    app.process_replay_events();

    if(app.replay_current_period == app.session.world_state.number_of_periods)
    {
        //end of the session
        return;
    }
    else
    {
        app.replay_current_period++;
    }

    app.replay_timeout = setTimeout(app.replay_mode_play, 1000);
},

/**
 * reset replay mode
 */
reset_replay: function reset_replay()
{
    app.replay_mode = "paused";
    if (app.replay_timeout) clearTimeout(app.replay_timeout);

    app.replay_current_period = 1;

    app.replay_load_world_state();

    app.the_feed = {};
    for(let i in app.session.world_state.groups)
    {
        app.the_feed[i] = [];
    }
    
},

/**
 * process replay events
 */
process_replay_events: function process_replay_events(update_current_location = false)
{
    let current_period = app.replay_current_period;

    for(let i in app.session_events[current_period])
    {   
        let event =  app.session_events[current_period][i];

        if(event.type == "target_location_update")
        {
            for(let i in event.data.target_locations)
            {
                app.session.world_state.session_players[i].target_location = JSON.parse(JSON.stringify(event.data.target_locations[i]));

                if(update_current_location)
                {
                    app.session.world_state.session_players[i].current_location = JSON.parse(JSON.stringify(event.data.current_locations[i]));
                }
            }
        }
        else
        {
            let data = {message:{message_data:JSON.parse(JSON.stringify(event.data)),
                                 message_type:"update_" + event.type},}
            app.take_message(data);
        }
        
    }

    app.session.world_state["current_experiment_phase"] = "Done";
    app.session.world_state["current_period"] = app.replay_current_period;
},


/**
 * advance period block
 */
advance_period: function advance_period(direction)
{
    let current_period_block = app.session.world_state.current_period_block;
    let parameter_set_periodblocks = app.session.parameter_set.parameter_set_periodblocks;
    let parameter_set_periodblocks_order = app.session.parameter_set.parameter_set_periodblocks_order;

    if(direction == 1)
    {
        for(let i=0; i<parameter_set_periodblocks_order.length; i++)
        {
            if(parameter_set_periodblocks_order[i] == current_period_block)
            {
                if(i < parameter_set_periodblocks_order.length - 1)
                {
                    app.replay_current_period = parameter_set_periodblocks[parameter_set_periodblocks_order[i+1]].period_start;
                }
                else
                {
                    return;
                }
            }
        }
    }
    else
    {
        for(let i=0; i<parameter_set_periodblocks_order.length; i++)
        {
            if(parameter_set_periodblocks_order[i] == current_period_block)
            {
                if(i > 0 && i < parameter_set_periodblocks_order.length)
                {
                    app.replay_current_period = parameter_set_periodblocks[parameter_set_periodblocks_order[i-1]].period_start;
                }
                else
                {
                    return;
                }
            }
        }
        
    }

    app.process_replay_events(true);
},