#version 410
layout(location = 0) in vec2 coord;
layout(location = 0) out vec4 frag_color;
 
layout(std140, binding = 0) uniform buf {
    float qt_Opacity;
    vec4 color;
} ubuf;


layout(binding = 1) uniform sampler2D src;

void main() {
    vec4 tex = texture(src, coord);
    float alpha = tex.a  * qt_Opacity;
    frag_color = vec4(ubuf.color.r * alpha, ubuf.color.g * alpha, ubuf.color.b * alpha, alpha);
}