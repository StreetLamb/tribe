/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChatMessage } from './ChatMessage';
import type { InterruptDecision } from './InterruptDecision';

export type TeamChat = {
    messages: Array<ChatMessage>;
    interrupt_decision?: (InterruptDecision | null);
};

