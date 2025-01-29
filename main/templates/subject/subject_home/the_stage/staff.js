/**
 * add scroll buttons to staff screen
 */
add_scroll_button: function add_scroll_button(button_size, name, text)
{
    let c = new PIXI.Container();

    let g = new PIXI.Graphics();
    
    g.rect(0, 0, button_size.w, button_size.h);

    
    g.fill({color:0xffffff});
    g.stroke(1, 0x000000);

    let label = new PIXI.Text({text:text, 
                               style:{fontFamily : 'Arial',
                                      fontWeight:'bold',
                                      fontSize: 28,       
                                      lineHeight : 14,                             
                                      align : 'center'}});
                                    
    label.pivot.set(label.width/2, label.height/2);
    label.x = button_size.w/2;
    label.y = button_size.h/2-3;

    c.addChild(g);
    c.addChild(label);

    c.pivot.set(button_size.w/2, button_size.h/2);
    c.x = button_size.x;
    c.y = button_size.y;
    c.eventMode = 'static';
    c.label = name;
    c.alpha = 0.5;

    c.on("pointerover", app.staff_screen_scroll_button_over);
    c.on("pointerout", app.staff_screen_scroll_button_out);

    pixi_app.stage.addChild(c);

    return c
},
