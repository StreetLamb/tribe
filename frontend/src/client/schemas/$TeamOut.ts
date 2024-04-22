/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TeamOut = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        description: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        id: {
            type: 'number',
            isRequired: true,
        },
        owner_id: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
