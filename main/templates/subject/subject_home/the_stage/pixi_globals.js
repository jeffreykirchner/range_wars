//pixi globals
let pixi_app = null;                           //pixi app   
let pixi_container_main = null;                //main container for pixi
let pixi_text_emitter = {};                    //text emitter json
let pixi_text_emitter_key = 0;
let pixi_fps_label = null;                     //fps label
let pixi_axis = null;                          //axis
let pixi_boxes = [];                           //boxes
let pixi_group_summary = null;                 //group summary graph
let pixi_selection_ranges = [];                //selection range graph

let pixi_left_handle = null;                   //left handle
let pixi_right_handle = null;                  //right handle

let x_axis_margin = 110;            //margin between x axis and canvas edge
let y_axis_margin = 60;             //margin between y axis and canvas edge
let other_margin = 10;              //margin between graph and canvas edge on right and top
let right_margin = 60;              //margin between graph and canvas edge on right

let axis_width = 0;
let axis_height = 0;
let axis_style = {fontFamily : 'Arial', fontSize: 16, fill : 0x000000, align : 'center'}
let control_style = {fontFamily : 'Arial', fontSize: 20, fill : "white", align : 'center'}

let origin_x = 0;
let origin_y = 0;
let box_width = 0;                  //width of a single box
