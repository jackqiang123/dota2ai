-- hero_phoenix.lua -- Phoenix 凤凰 -- v2.0.0 BotLib 英雄文件 (由 tools/generate.py 生成, 不要手改)。
-- 结构 (方法来源: OHA ARCHITECTURE.md 第 3 节描述的分段, 实现自己写):
-- 天赋表 / 加点表 / 分位置出装表 / 技能名表 / SkillsComplement() + ConsiderX()。
-- 焦点英雄: 真实 Consider 逻辑 (见 tools/focus_heroes.py); 其余英雄: 通用类型驱动 fallback。
local Skill = require(GetScriptDirectory() .. "/engine/skill")
local Micro = require(GetScriptDirectory() .. "/engine/micro")
local Team = require(GetScriptDirectory() .. "/engine/team")
local Heroes = require(GetScriptDirectory() .. "/data/heroes")
local X = {}
X.KEY = "phoenix"
X.TALENTS = { [10] = 0, [15] = 0, [20] = 0, [25] = 0 }
X.SKILL_BUILD = {1, 2, 3, 1, 2, 4, 3, 1, 2, 3, 4, 1, 2, 3, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0}
X.sBuyList = {}
X.sBuyList["pos_1"] = {"item_tango", "item_flask", "item_quelling_blade", "item_wraith_band", "item_power_treads", "item_magic_wand", "item_shivas_guard", "item_black_king_bar", "item_radiance", "item_aghanims_shard", "item_butterfly", "item_satanic", "item_abyssal_blade"}
X.sBuyList["pos_2"] = {"item_tango", "item_flask", "item_null_talisman", "item_bottle", "item_power_treads", "item_magic_wand", "item_shivas_guard", "item_black_king_bar", "item_radiance", "item_aghanims_shard", "item_octarine_core", "item_scythe_of_vyse"}
X.sBuyList["pos_3"] = {"item_tango", "item_flask", "item_bracer", "item_phase_boots", "item_magic_wand", "item_shivas_guard", "item_black_king_bar", "item_radiance", "item_aghanims_shard", "item_assault"}
X.sBuyList["pos_4"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_tranquil_boots", "item_shivas_guard", "item_black_king_bar", "item_radiance", "item_aghanims_shard", "item_aghanims_scepter", "item_lotus_orb"}
X.sBuyList["pos_5"] = {"item_tango", "item_flask", "item_clarity", "item_ward_observer", "item_magic_wand", "item_arcane_boots", "item_shivas_guard", "item_black_king_bar", "item_radiance", "item_aghanims_shard", "item_aghanims_scepter", "item_force_staff", "item_glimmer_cape"}
X.sSellList = {"item_tango", "item_flask", "item_clarity", "item_quelling_blade", "item_wraith_band", "item_bracer", "item_null_talisman"}
X.ABILITIES = {}
-- 通用版: 无专属 Consider, 直接走 v1.1 的类型驱动 fallback。
function X.SkillsComplement(bot, snap)
  if bot == nil or snap == nil then return false end
  local heroData = Heroes[X.KEY]
  if heroData == nil then return false end
  return Micro.TryCastByType(bot, snap, heroData)
end
return X
