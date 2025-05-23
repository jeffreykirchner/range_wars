{% load static %}

/**
 * update the pixi players with new info
 */
setup_pixi: function setup_pixi(){    
    app.reset_pixi_app();

    PIXI.Assets.add({alias:'dash_tex', src:'{% static "dash_1.png"%}'});
    PIXI.Assets.add({alias:'pattern_1_tex', src:'{% static "pattern1.png"%}'});
    PIXI.Assets.add({alias:'pattern_2_tex', src:'{% static "pattern2.png"%}'});
    PIXI.Assets.add({alias:'question_mark_text', src:'{% static "question_mark.png"%}'});
    
    const textures_promise = PIXI.Assets.load(['dash_tex', 'pattern_1_tex', 'pattern_2_tex', 'question_mark_text']);

    textures_promise.then((textures) => {
        app.setup_pixi_sheets(textures);
       
        if(app.pixi_mode!="subject")
        {
          
        }
        else
        {
     
        }
    });

    
    pixi_text_emitter = {};
    pixi_text_emitter_key = 0;

},

reset_pixi_app: async function reset_pixi_app(){    

    app.stage_width = app.session.parameter_set.world_width;
    app.stage_height = app.session.parameter_set.world_height;

    let canvas = document.getElementById('sd_graph_id');

    pixi_app = new PIXI.Application()

    await pixi_app.init({resizeTo : canvas,
                         backgroundColor : 0xFFFFFF,
                         autoResize: true,
                         antialias: false,
                         resolution: 1,
                         canvas: canvas });

    // The stage will handle the move events
    // pixi_app.stage.hitArea = pixi_app.screen;

    app.canvas_width = canvas.width;
    app.canvas_height = canvas.height;

    app.last_collision_check = Date.now();
},

/** load pixi sprite sheets
*/
setup_pixi_sheets: function setup_pixi_sheets(textures){

    app.pixi_textures = textures;

    app.setup_main_container();
   
    //subject controls
    if(app.pixi_mode=="subject")
    {
       
    }
    else
    {
       
    }

    // staff controls
    if(app.pixi_mode=="staff"){
        
    }

    //axis
    app.setup_axis();

    //treatment
    app.setup_treatment();
    app.update_treatment();
    app.setup_selection_range();
    app.setup_group_summary();
    
    if(app.pixi_mode=="subject")
    {
        app.setup_control_handles();
        app.update_handle_visibility();
    }

    {%if DEBUG or session.parameter_set.test_mode%}
    //fps counter
    let text_style = {
        fontFamily: 'Arial',
        fontSize: 14,
        fill: {color:'black'},
        align: 'left',
    };
    let fps_label = new PIXI.Text({text:"0 fps", 
                                   style:text_style});

    pixi_fps_label = fps_label;
    pixi_fps_label.position.set(10, app.canvas_height-25);
    // pixi_app.stage.addChild(pixi_fps_label);   
    {%endif%}

    //start game loop
    pixi_app.ticker.add(app.game_loop);
},

/**
 * setup the main container
 */
setup_main_container: function setup_main_container(){
    //remove old container
    if(pixi_container_main)
    {
        pixi_app.stage.removeChild(pixi_container_main);
        pixi_container_main.destroy();
    }

    pixi_container_main = new PIXI.Container();
    pixi_container_main.sortableChildren = true;
    pixi_app.stage.addChild(pixi_container_main);
},

/**
 * game loop for pixi
 */
game_loop: function game_loop(delta)
{

    app.move_text_emitters(delta.deltaTime);

    if(app.pixi_mode=="subject" && app.session.started)
    {   

    }
    
    if(app.pixi_mode=="staff")
    {

    }  
    
    {%if DEBUG%}
    pixi_fps_label.text = Math.round(pixi_app.ticker.FPS) + " FPS";
    {%endif%}

    //tick tock
    if(Date.now() - app.pixi_tick_tock.time >= 300)
    {
        app.pixi_tick_tock.time = Date.now();
        if(app.pixi_tick_tock.value == "tick") 
            app.pixi_tick_tock.value = "tock";
        else
            app.pixi_tick_tock.value = "tick";

        if(app.pixi_tick_tock.value == "tick")
        {
            //flash the loss text
            for(let i=0;i<pixi_loss_text.length;i++)
            {
                pixi_loss_text[i].visible = true;
            }
        }
        else
        {
            //hide the loss text
            for(let i=0;i<pixi_loss_text.length;i++)
            {
                pixi_loss_text[i].visible = false;
            }
        }
    }
},