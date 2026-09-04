"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2026-09-03 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create market_data table
    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('market_volume', sa.Float(), nullable=False),
        sa.Column('global_co2', sa.Float(), nullable=True),
        sa.Column('renewable_electricity_share', sa.Float(), nullable=True),
        sa.Column('renewable_production', sa.Float(), nullable=True),
        sa.Column('global_gdp_growth', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year')
    )
    op.create_index(op.f('ix_market_data_id'), 'market_data', ['id'], unique=False)
    op.create_index(op.f('ix_market_data_year'), 'market_data', ['year'], unique=True)

    # Create country_intelligence table
    op.create_table(
        'country_intelligence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('iso', sa.String(length=10), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('co2', sa.Float(), nullable=True),
        sa.Column('per_capita_co2', sa.Float(), nullable=True),
        sa.Column('renewable_electricity_share', sa.Float(), nullable=True),
        sa.Column('renewable_production', sa.Float(), nullable=True),
        sa.Column('gdp_growth', sa.Float(), nullable=True),
        sa.Column('carbon_rate_2023', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country', 'year', name='uq_country_year')
    )
    op.create_index(op.f('ix_country_intelligence_country'), 'country_intelligence', ['country'], unique=False)
    op.create_index('ix_country_intelligence_country_year', 'country_intelligence', ['country', 'year'], unique=False)
    op.create_index(op.f('ix_country_intelligence_id'), 'country_intelligence', ['id'], unique=False)
    op.create_index(op.f('ix_country_intelligence_iso'), 'country_intelligence', ['iso'], unique=False)
    op.create_index(op.f('ix_country_intelligence_year'), 'country_intelligence', ['year'], unique=False)

    # Create company_trading table
    op.create_table(
        'company_trading',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.String(length=20), nullable=False),
        sa.Column('industry_type', sa.String(length=50), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('energy_demand_mwh', sa.Float(), nullable=False),
        sa.Column('fuel_type', sa.String(length=50), nullable=False),
        sa.Column('emission_produced_tco2', sa.Float(), nullable=False),
        sa.Column('emission_allowance_tco2', sa.Float(), nullable=False),
        sa.Column('carbon_price_usd_per_t', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('credits_traded_tco2', sa.Float(), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('compliance_cost_usd', sa.Float(), nullable=False),
        sa.Column('optimization_scenario', sa.String(length=50), nullable=True),
        sa.Column('carbon_cost_savings_usd', sa.Float(), nullable=True),
        sa.Column('target_trade_action', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_company_trading_company_date', 'company_trading', ['company_id', 'date'], unique=False)
    op.create_index(op.f('ix_company_trading_company_id'), 'company_trading', ['company_id'], unique=False)
    op.create_index(op.f('ix_company_trading_date'), 'company_trading', ['date'], unique=False)
    op.create_index(op.f('ix_company_trading_id'), 'company_trading', ['id'], unique=False)
    op.create_index('ix_company_trading_industry', 'company_trading', ['industry_type'], unique=False)

    # Create country_scores table
    op.create_table(
        'country_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('iso', sa.String(length=10), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_category', sa.String(length=20), nullable=True),
        sa.Column('comp_co2', sa.Float(), nullable=True),
        sa.Column('comp_per_cap', sa.Float(), nullable=True),
        sa.Column('comp_renew_weak', sa.Float(), nullable=True),
        sa.Column('comp_gdp_weak', sa.Float(), nullable=True),
        sa.Column('comp_policy_weak', sa.Float(), nullable=True),
        sa.Column('opportunity_score', sa.Float(), nullable=True),
        sa.Column('opportunity_category', sa.String(length=20), nullable=True),
        sa.Column('comp_renew_elec', sa.Float(), nullable=True),
        sa.Column('comp_renew_prod', sa.Float(), nullable=True),
        sa.Column('comp_transition', sa.Float(), nullable=True),
        sa.Column('comp_econ_res', sa.Float(), nullable=True),
        sa.Column('comp_policy_enable', sa.Float(), nullable=True),
        sa.Column('flag_renewable_imputed', sa.String(length=10), nullable=True),
        sa.Column('flag_gdp_imputed', sa.String(length=10), nullable=True),
        sa.Column('flag_carbon_rate_imputed', sa.String(length=10), nullable=True),
        sa.Column('flag_renew_elec_imputed', sa.String(length=10), nullable=True),
        sa.Column('flag_renew_prod_imputed', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country', 'year', name='uq_country_score_year')
    )
    op.create_index(op.f('ix_country_scores_country'), 'country_scores', ['country'], unique=False)
    op.create_index('ix_country_scores_country_year', 'country_scores', ['country', 'year'], unique=False)
    op.create_index(op.f('ix_country_scores_id'), 'country_scores', ['id'], unique=False)
    op.create_index('ix_country_scores_opportunity', 'country_scores', ['opportunity_score'], unique=False)
    op.create_index('ix_country_scores_risk', 'country_scores', ['risk_score'], unique=False)

    # Create forecast_results table
    op.create_table(
        'forecast_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('market_volume', sa.Float(), nullable=False),
        sa.Column('series', sa.String(length=20), nullable=False),
        sa.Column('market_value_model', sa.String(length=50), nullable=True),
        sa.Column('market_volume_model', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year')
    )
    op.create_index(op.f('ix_forecast_results_id'), 'forecast_results', ['id'], unique=False)
    op.create_index(op.f('ix_forecast_results_year'), 'forecast_results', ['year'], unique=True)

    # Create scenario_results table
    op.create_table(
        'scenario_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('carbon_price_change_pct', sa.Float(), nullable=False),
        sa.Column('emissions_change_pct', sa.Float(), nullable=False),
        sa.Column('renewable_share_change_pct', sa.Float(), nullable=False),
        sa.Column('gdp_growth_change_pct', sa.Float(), nullable=False),
        sa.Column('baseline_market_value', sa.Float(), nullable=False),
        sa.Column('baseline_market_volume', sa.Float(), nullable=False),
        sa.Column('scenario_market_value', sa.Float(), nullable=False),
        sa.Column('scenario_market_volume', sa.Float(), nullable=False),
        sa.Column('value_change', sa.Float(), nullable=False),
        sa.Column('value_change_pct', sa.Float(), nullable=False),
        sa.Column('volume_change', sa.Float(), nullable=False),
        sa.Column('volume_change_pct', sa.Float(), nullable=False),
        sa.Column('model_info', sa.Text(), nullable=True),
        sa.Column('warnings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_results_created_at'), 'scenario_results', ['created_at'], unique=False)
    op.create_index(op.f('ix_scenario_results_id'), 'scenario_results', ['id'], unique=False)

    # Create prediction_requests table
    op.create_table(
        'prediction_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('industry_type', sa.String(length=50), nullable=False),
        sa.Column('fuel_type', sa.String(length=50), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('energy_demand_mwh', sa.Float(), nullable=False),
        sa.Column('emission_produced_tco2', sa.Float(), nullable=False),
        sa.Column('emission_allowance_tco2', sa.Float(), nullable=False),
        sa.Column('carbon_price_usd_per_t', sa.Float(), nullable=False),
        sa.Column('compliance_cost_usd', sa.Float(), nullable=False),
        sa.Column('predicted_action', sa.String(length=10), nullable=False),
        sa.Column('probability', sa.Float(), nullable=False),
        sa.Column('confidence', sa.String(length=20), nullable=False),
        sa.Column('model_used', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_requests_created_at'), 'prediction_requests', ['created_at'], unique=False)
    op.create_index(op.f('ix_prediction_requests_id'), 'prediction_requests', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_prediction_requests_id'), table_name='prediction_requests')
    op.drop_index(op.f('ix_prediction_requests_created_at'), table_name='prediction_requests')
    op.drop_table('prediction_requests')
    
    op.drop_index(op.f('ix_scenario_results_id'), table_name='scenario_results')
    op.drop_index(op.f('ix_scenario_results_created_at'), table_name='scenario_results')
    op.drop_table('scenario_results')
    
    op.drop_index(op.f('ix_forecast_results_year'), table_name='forecast_results')
    op.drop_index(op.f('ix_forecast_results_id'), table_name='forecast_results')
    op.drop_table('forecast_results')
    
    op.drop_index('ix_country_scores_risk', table_name='country_scores')
    op.drop_index('ix_country_scores_opportunity', table_name='country_scores')
    op.drop_index(op.f('ix_country_scores_id'), table_name='country_scores')
    op.drop_index('ix_country_scores_country_year', table_name='country_scores')
    op.drop_index(op.f('ix_country_scores_country'), table_name='country_scores')
    op.drop_table('country_scores')
    
    op.drop_index('ix_company_trading_industry', table_name='company_trading')
    op.drop_index(op.f('ix_company_trading_id'), table_name='company_trading')
    op.drop_index(op.f('ix_company_trading_date'), table_name='company_trading')
    op.drop_index(op.f('ix_company_trading_company_id'), table_name='company_trading')
    op.drop_index('ix_company_trading_company_date', table_name='company_trading')
    op.drop_table('company_trading')
    
    op.drop_index(op.f('ix_country_intelligence_year'), table_name='country_intelligence')
    op.drop_index(op.f('ix_country_intelligence_iso'), table_name='country_intelligence')
    op.drop_index(op.f('ix_country_intelligence_id'), table_name='country_intelligence')
    op.drop_index('ix_country_intelligence_country_year', table_name='country_intelligence')
    op.drop_index(op.f('ix_country_intelligence_country'), table_name='country_intelligence')
    op.drop_table('country_intelligence')
    
    op.drop_index(op.f('ix_market_data_year'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_id'), table_name='market_data')
    op.drop_table('market_data')
