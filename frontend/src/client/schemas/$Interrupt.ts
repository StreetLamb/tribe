/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Interrupt = {
    properties: {
        decision: {
            type: 'InterruptDecision',
            isRequired: true,
        },
        rejection_message: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
