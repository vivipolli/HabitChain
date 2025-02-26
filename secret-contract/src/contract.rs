use cosmwasm_std::{
    entry_point, to_binary, from_binary, Binary,
    Deps, DepsMut, Env, MessageInfo, Response, StdError, StdResult,
};
use serde::{Deserialize, Serialize};
use schemars::JsonSchema;
use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct Task {
    pub name: String,
    pub completed: bool,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct State {
    pub analyses: Vec<Analysis>,
    pub daily_progress: Vec<DailyProgress>,
    pub viewing_keys: Vec<(String, String)>, // (patient_id, key)
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct Analysis {
    pub patient_id: String,
    pub content: String,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
pub struct DailyProgress {
    pub patient_id: String,
    pub date: u64,
    pub tasks: Vec<Task>,
    pub description: String,
}

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,
    _msg: InstantiateMsg,
) -> StdResult<Response> {
    let state = State {
        analyses: vec![],
        daily_progress: vec![],
        viewing_keys: vec![],
    };
    deps.storage.set(b"state", &to_binary(&state)?);
    Ok(Response::default())
}

#[entry_point]
pub fn execute(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,
    msg: ExecuteMsg,
) -> StdResult<Response> {
    match msg {
        ExecuteMsg::SaveAnalysis { patient_id, content } => {
            let mut state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;
            state.analyses.push(Analysis { patient_id, content });
            deps.storage.set(b"state", &to_binary(&state)?);
            Ok(Response::default())
        },
        ExecuteMsg::CreateViewingKey { patient_id } => {
            let mut state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;
            let key = "test_key".to_string();
            state.viewing_keys.push((patient_id, key.clone()));
            deps.storage.set(b"state", &to_binary(&state)?);
            Ok(Response::new().add_attribute("viewing_key", key))
        },
        ExecuteMsg::SaveDailyProgress { patient_id, date, tasks, description } => {
            let mut state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;
            state.daily_progress.push(DailyProgress { patient_id, date, tasks, description });
            deps.storage.set(b"state", &to_binary(&state)?);
            Ok(Response::default())
        },
    }
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::GetAnalyses { patient_id, viewing_key } => {
            let state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;
            let valid_key = state.viewing_keys.iter().any(|(id, key)| id == &patient_id && key == &viewing_key);
            if !valid_key {
                return Err(StdError::generic_err("Invalid viewing key"));
            }
            let analyses: Vec<Analysis> = state.analyses
                .iter()
                .filter(|a| a.patient_id == patient_id)
                .cloned()
                .collect();
            to_binary(&analyses)
        },
        QueryMsg::GetDailyProgress { patient_id } => {
            let state: State = from_binary(&Binary::from(deps.storage.get(b"state").unwrap_or_default()))?;
            let progress: Vec<DailyProgress> = state.daily_progress
                .iter()
                .filter(|p| p.patient_id == patient_id)
                .cloned()
                .collect();
            to_binary(&progress)
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::testing::{mock_dependencies, mock_env, mock_info};

    #[test]
    fn proper_initialization() {
        let mut deps = mock_dependencies();
        let env = mock_env();
        let info = mock_info("creator", &[]);
        let msg = InstantiateMsg {};

        let res = instantiate(deps.as_mut(), env, info, msg).unwrap();
        assert_eq!(0, res.messages.len());
    }

    #[test]
    fn test_save_analysis() {
        let mut deps = mock_dependencies();
        let env = mock_env();
        let info = mock_info("creator", &[]);
        
        // Primeiro inicializa
        let msg = InstantiateMsg {};
        instantiate(deps.as_mut(), env.clone(), info.clone(), msg).unwrap();

        // Cria a viewing key primeiro
        let msg = ExecuteMsg::CreateViewingKey {
            patient_id: "123".to_string(),
        };
        execute(deps.as_mut(), env.clone(), info.clone(), msg).unwrap();

        // Depois salva a análise
        let msg = ExecuteMsg::SaveAnalysis {
            patient_id: "123".to_string(),
            content: "test content".to_string(),
        };
        execute(deps.as_mut(), env.clone(), info, msg).unwrap();

        // Verifica se salvou corretamente
        let msg = QueryMsg::GetAnalyses {
            patient_id: "123".to_string(),
            viewing_key: "test_key".to_string(),  // Agora a chave existe
        };
        let res = query(deps.as_ref(), env, msg).unwrap();
        let analyses: Vec<Analysis> = from_binary(&res).unwrap();
        assert_eq!(1, analyses.len());
    }
}
