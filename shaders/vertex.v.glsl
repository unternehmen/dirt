#version 120
attribute vec2 coord2d;
attribute vec2 texcoord;
uniform mat4 transform;
varying vec2 f_texcoord;
void main(void) {
    gl_Position = transform * vec4(coord2d, 0.0, 1.0);
    f_texcoord = texcoord;
}
