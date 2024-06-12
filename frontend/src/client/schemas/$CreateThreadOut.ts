/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CreateThreadOut = {
    properties: {
        id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        query: {
            type: 'string',
            isRequired: true,
        },
        updated_at: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        last_checkpoint: {
            type: 'any-of',
            contains: [{
                type: 'CheckpointOut',
            }, {
                type: 'null',
            }],
            isRequired: true,
        },
    },
} as const;
