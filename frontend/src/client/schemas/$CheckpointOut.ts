/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $CheckpointOut = {
    properties: {
        thread_id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        thread_ts: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        checkpoint: {
            type: 'binary',
            isRequired: true,
            format: 'binary',
        },
        created_at: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
    },
} as const;
