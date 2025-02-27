use cosmwasm_schema::{cw_serde, QueryResponses};
use crate::contract::{Task, Analysis, DailyProgress};

#[cw_serde]
pub struct InstantiateMsg {}

#[cw_serde]
pub enum ExecuteMsg {
    SaveAnalysis { patient_id: String, content: String },
    CreateViewingKey { patient_id: String },
    SaveDailyProgress { patient_id: String, date: u64, tasks: Vec<Task>, description: String },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Vec<Analysis>)]
    GetAnalyses { patient_id: String, viewing_key: String },
    #[returns(Vec<DailyProgress>)]
    GetDailyProgress { patient_id: String },
}
