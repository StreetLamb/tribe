/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $GraphResponse = {
    properties: {
        kind: {
            type: 'string',
            isRequired: true,
        },
        id: {
            type: 'string',
            isRequired: true,
        },
        name: {
            type: 'string',
            isRequired: true,
        },
        content: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'dictionary',
                contains: {
                    properties: {
                    },
                },
            }],
            isRequired: true,
        },
        next: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        parent_ids: {
            type: 'array',
            contains: {
                type: 'string',
            },
            isRequired: true,
        },
    },
} as const;
