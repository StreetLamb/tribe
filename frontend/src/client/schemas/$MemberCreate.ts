/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $MemberCreate = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        backstory: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        role: {
            type: 'string',
            isRequired: true,
        },
        type: {
            type: 'string',
            isRequired: true,
        },
        owner_of: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        position_x: {
            type: 'number',
            isRequired: true,
        },
        position_y: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
