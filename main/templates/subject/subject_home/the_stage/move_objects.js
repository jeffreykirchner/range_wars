/**
 * move the object towards its target location
 */
move_object: function move_object(delta, obj, move_speed)
{
    let temp_move_speed = (move_speed * delta);

    let temp_current_location = Object.assign({}, obj.current_location);

    let target_location_local = Object.assign({}, obj.target_location);
    if("nav_point" in obj && obj.nav_point) 
    target_location_local = Object.assign({}, obj.nav_point);

    let temp_angle = Math.atan2(target_location_local.y - obj.current_location.y,
                                target_location_local.x - obj.current_location.x)

    //y
    if(Math.abs(target_location_local.y - obj.current_location.y) < temp_move_speed)
        obj.current_location.y = target_location_local.y;
    else
        obj.current_location.y += temp_move_speed * Math.sin(temp_angle);
 
    //x
    if(Math.abs(target_location_local.x - obj.current_location.x) < temp_move_speed)
        obj.current_location.x = target_location_local.x;
    else
        obj.current_location.x += temp_move_speed * Math.cos(temp_angle);  

    
},

move_avatar: function move_avatar(delta, player_id)
{
    
    let temp_move_speed = (parseFloat(app.session.parameter_set.avatar_move_speed) * delta);
    let obj = app.session.world_state.session_players[player_id];
    let parameter_set_group = app.session.parameter_set.parameter_set_players[obj.parameter_set_player_id].parameter_set_group;
    let container=pixi_avatars[player_id].bounding_box
    let scale = app.session.parameter_set.avatar_scale;

    let temp_current_location = Object.assign({}, obj.current_location);

    let target_location_local = Object.assign({}, obj.target_location);
    if("nav_point" in obj && obj.nav_point) 
    target_location_local = Object.assign({}, obj.nav_point);

    let temp_angle = Math.atan2(target_location_local.y - obj.current_location.y,
                                target_location_local.x - obj.current_location.x)

    //y
    if(Math.abs(target_location_local.y - obj.current_location.y) < temp_move_speed)
        obj.current_location.y = target_location_local.y;
    else
        obj.current_location.y += temp_move_speed * Math.sin(temp_angle);
 
    //x
    if(Math.abs(target_location_local.x - obj.current_location.x) < temp_move_speed)
        obj.current_location.x = target_location_local.x;
    else
        obj.current_location.x += temp_move_speed * Math.cos(temp_angle);  

},