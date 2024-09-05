#version 410

layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 coord; 

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
} ubuf;

void main() {
    coord = qt_MultiTexCoord0;
    gl_Position = ubuf.qt_Matrix * qt_Vertex;
}