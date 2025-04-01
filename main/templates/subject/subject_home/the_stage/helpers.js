/**
 * do random self test actions
 */
random_number: function random_number(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
},

random_string: function random_string(min_length, max_length){

    let s = "";
    let r = app.random_number(min_length, max_length);

    for(let i=0;i<r;i++)
    {
        let v = app.random_number(48, 122);
        s += String.fromCharCode(v);
    }

    return s;
},

/**
 * get the parameter set player from the player id
*/
get_parameter_set_player_from_player_id: function get_parameter_set_player_from_player_id(player_id)
{
    try 
    {
        let parameter_set_player_id = app.session.world_state.session_players[player_id].parameter_set_player_id;
        return app.session.parameter_set.parameter_set_players[parameter_set_player_id];
    }
    catch (error) {
        return {id_label:null};
    }
},

/**
 * get current treatment
 */
get_current_treatment: function get_current_treatment()
{
    if(!app.session.started)
    {
        return null;
    }
    
    let parameter_set_period_block = app.get_current_parameter_set_period_block();    
    return app.session.parameter_set.parameter_set_treatments[parameter_set_period_block.parameter_set_treatment];
},

/**
 * get current period block
 */
get_current_period_block: function get_current_period_block()
{
    return app.session.world_state.period_blocks[app.session.world_state.current_period_block];
},

/**
 * get current parameter set period block
 */
get_current_parameter_set_period_block: function get_current_parameter_set_period_block()
{
    return app.session.parameter_set.parameter_set_periodblocks[app.session.world_state.current_period_block];
},