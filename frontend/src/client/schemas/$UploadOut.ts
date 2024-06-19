/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $UploadOut = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        id: {
            type: 'number',
            isRequired: true,
        },
        path: {
            type: 'string',
            isRequired: true,
        },
        last_modified: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
    },
} as const;
