#version 330 core

/**
 * Shader for rendering an infinite world grid.
 *
 * @details The code is taken from Marie at:
 * <a href="http://asliceofrendering.com/scene%20helper/2020/01/05/InfiniteGrid/">
 * asliceofrendering.com
 * </a>
 * License: <a href="https://github.com/BugzTroll/bugztroll.github.io/blob/master/LICENSE">
 * MIT License </a>
 *
 * @details It has been adjusted to suit the needs for this project.
 */

layout(location = 0) in vec3 position;

/*
layout(location = 1) out vec3 nearPoint;
layout(location = 2) out vec3 farPoint;
*/

out vec3 nearPoint;
out vec3 farPoint;

out mat4 fragProj;
out mat4 fragView;

uniform mat4 u_projection;
uniform mat4 u_view;

/**
 * Unproject point from clip space to world space.
 */
vec3 UnprojectPoint(float x, float y, float z, mat4 view, mat4 projection) {
    mat4 viewInv = inverse(view);
    mat4 projInv = inverse(projection);
    vec4 unprojectedPoint =  viewInv * projInv * vec4(x, y, z, 1.0);
    return unprojectedPoint.xyz / unprojectedPoint.w;
}

// normal vertice projection
void main() {
    fragProj = u_projection;
    fragView = u_view;

    nearPoint = UnprojectPoint(position.x, position.y, 0.0, u_view, u_projection).xyz; // unprojecting on the near plane
    farPoint = UnprojectPoint(position.x, position.y, 1.0, u_view, u_projection).xyz; // unprojecting on the far plane
    gl_Position = vec4(position, 1.0);
}
