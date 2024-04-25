/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Skill } from './Skill';

export type MemberUpdate = {
    name?: (string | null);
    backstory?: (string | null);
    role?: (string | null);
    type?: (string | null);
    owner_of?: (number | null);
    position_x?: (number | null);
    position_y?: (number | null);
    source?: (number | null);
    belongs_to?: (number | null);
    skills?: (Array<Skill> | null);
};

