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

let x_axis_margin = 100;             //margin between x axis and canvas edge
let y_axis_margin = 50;             //margin between y axis and canvas edge
let other_margin = 10;              //margin between graph and canvas edge on right and top

let axis_width = 0;
let axis_height = 0;
let axis_style = {fontFamily : 'Arial', fontSize: 16, fill : 0x000000, align : 'center'}

let origin_x = 0;
let origin_y = 0;
let box_width = 0;                  //width of a single box

let current_treatment = null;       //current treatment
let current_group = 1;              //current group
