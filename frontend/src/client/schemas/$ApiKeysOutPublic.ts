/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ApiKeysOutPublic = {
    properties: {
        data: {
            type: 'array',
            contains: {
                type: 'ApiKeyOutPublic',
            },
            isRequired: true,
        },
        count: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
