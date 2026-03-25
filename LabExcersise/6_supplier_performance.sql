-- drop table supplier_data;
-- drop table supplier;

-- 1) **************************************************
-- Create the tables to store the actual and vector data
-- *****************************************************

-- 1) create supplier performance table
CREATE TABLE supplier_data (
    supplier_id TEXT,
    supplier_name TEXT,
    category TEXT,
    region TEXT,
    on_time_delivery_pct NUMERIC,
    quality_score NUMERIC,
    cost_variance_pct NUMERIC,
    avg_lead_time_days NUMERIC,
    defect_rate_pct NUMERIC,
    compliance_score NUMERIC,
    risk_score NUMERIC,
    total_orders INT,
    avg_order_value_usd NUMERIC,
    late_deliveries INT,
    contract_breach_count INT,
    supplier_performance_score NUMERIC,
    supplier_segment TEXT
);

select count(1) from supplier_data;

select * from supplier_data;

-- 3) Create table to store the text from the actual table
CREATE TABLE IF NOT EXISTS supplier 
(
  supplier_id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  content_tsv tsvector GENERATED ALWAYS AS ( to_tsvector('english', coalesce(content,''))) STORED,
  metadata JSONB NOT NULL,
  embedding VECTOR(1536)
);

select * from supplier;

-- ****************************************************
-- 2) Create the list of Indexes for each search mechanism
-- ****************************************************

-- 1) Lexical Search
CREATE INDEX IF NOT EXISTS idx_supplier_content_tsv ON supplier USING GIN (content_tsv);

-- 2) Fast metadata filtering (optional but useful): GIN: Generalized Inverted Index
CREATE INDEX IF NOT EXISTS idx_supplier_metadata ON supplier USING GIN (metadata);

-- 3) Vector index for similarity search (choose one)
CREATE INDEX IF NOT EXISTS idx_supplier_embedding ON supplier USING hnsw (embedding vector_cosine_ops);

-- ******************************************
-- 3) Populate the data for the above tables
-- ******************************************

-- 1) table: supplier_data
-- 	  Import data "supplier_performance.csv" on this table

-- 2) table: supplier
-- 		Run the below script to upload the string and metadata data

insert into supplier(supplier_id, content, metadata)
(
	SELECT supplier_id, 
			CONCAT
			(
				'Supplier: ', supplier_id, ' in ', category, ', ', region, '. ',
			
				'On-time delivery: ', on_time_delivery_pct, '%. ',
				'Delivery reliability band: ',
				  CASE
					WHEN on_time_delivery_pct >= 95 THEN 'Excellent'
					WHEN on_time_delivery_pct >= 90 THEN 'Very Good'
					WHEN on_time_delivery_pct >= 85 THEN 'Good'
					WHEN on_time_delivery_pct >= 75 THEN 'Moderate'
					ELSE 'Poor'
				  END, '. ',
			
				'Quality score: ', quality_score, '/100. ',
				'Quality band: ',
				  CASE
					WHEN quality_score >= 90 THEN 'Excellent'
					WHEN quality_score >= 80 THEN 'Good'
					WHEN quality_score >= 70 THEN 'Average'
					ELSE 'Poor'
				  END, '. ',
			
				'Cost variance: ', cost_variance_pct, '%. ',
				'Cost stability band: ',
				  CASE
					WHEN ABS(cost_variance_pct) <= 2 THEN 'Stable'
					WHEN ABS(cost_variance_pct) <= 5 THEN 'Slightly Variable'
					WHEN ABS(cost_variance_pct) <= 10 THEN 'Variable'
					ELSE 'Highly Variable'
				  END, '. ',
			
				'Average lead time: ', avg_lead_time_days, ' days. ',
				'Lead time band: ',
				  CASE
					WHEN avg_lead_time_days <= 14 THEN 'Fast'
					WHEN avg_lead_time_days <= 30 THEN 'Moderate'
					WHEN avg_lead_time_days <= 60 THEN 'Slow'
					ELSE 'Very Slow'
				  END, '. ',
			
				'Defect rate: ', defect_rate_pct, '%. ',
				'Defect band: ',
				  CASE
					WHEN defect_rate_pct <= 1 THEN 'Excellent'
					WHEN defect_rate_pct <= 3 THEN 'Good'
					WHEN defect_rate_pct <= 5 THEN 'Moderate'
					ELSE 'High'
				  END, '. ',
			
				'Compliance score: ', compliance_score, '/100. ',
				'Compliance band: ',
				  CASE
					WHEN compliance_score >= 95 THEN 'Excellent'
					WHEN compliance_score >= 85 THEN 'Strong'
					WHEN compliance_score >= 70 THEN 'Adequate'
					ELSE 'Weak'
				  END, '. ',
			
				'Risk score: ', risk_score, ' (0-100; higher means higher risk). ',
				'Risk band: ',
				  CASE
					WHEN risk_score >= 80 THEN 'High'
					WHEN risk_score >= 60 THEN 'Medium'
					WHEN risk_score >= 40 THEN 'Low'
					ELSE 'Very Low'
				  END, '. ',
			
				'Total orders: ', total_orders, '. ',
				'Average order value: USD ', avg_order_value_usd, '. ',
			
				'Late deliveries: ', late_deliveries, '. ',
				'Late delivery rate: ',
				  CASE
					WHEN total_orders IS NULL OR total_orders = 0 THEN 'NA'
					ELSE TO_CHAR(ROUND(100.0 * late_deliveries::numeric / total_orders::numeric, 2), 'FM999990.00')
				  END, '%. ',
				'Delivery issues flag: ',
				  CASE
					WHEN (total_orders > 0 AND (100.0 * late_deliveries::numeric / total_orders::numeric) >= 20)
						 OR on_time_delivery_pct < 85
					THEN 'Yes' ELSE 'No'
				  END, '. ',
			
				'Contract breach count: ', contract_breach_count, '. ',
				'Breach risk band: ',
				  CASE
					WHEN contract_breach_count >= 3 THEN 'High'
					WHEN contract_breach_count >= 1 THEN 'Medium'
					ELSE 'Low'
				  END, '. ',
			
				'Supplier performance score: ', supplier_performance_score, '. ',
				'Performance band: ',
				  CASE
					WHEN supplier_performance_score >= 85 THEN 'Excellent'
					WHEN supplier_performance_score >= 70 THEN 'Good'
					WHEN supplier_performance_score >= 55 THEN 'Average'
					ELSE 'Poor'
				  END, '. '
			) as content,
			
			-- metadata
			jsonb_build_object(
	    'supplier_id', supplier_id,
	    'category', category,
	    'region', region,
	    'supplier_segment', supplier_segment,
	
	    'delivery_reliability_band',
	      CASE
	        WHEN on_time_delivery_pct >= 95 THEN 'Excellent'
	        WHEN on_time_delivery_pct >= 90 THEN 'Very Good'
	        WHEN on_time_delivery_pct >= 85 THEN 'Good'
	        WHEN on_time_delivery_pct >= 75 THEN 'Moderate'
	        ELSE 'Poor'
	      END,
	
	    'quality_band',
	      CASE
	        WHEN quality_score >= 90 THEN 'Excellent'
	        WHEN quality_score >= 80 THEN 'Good'
	        WHEN quality_score >= 70 THEN 'Average'
	        ELSE 'Poor'
	      END,
	
	    'cost_stability_band',
	      CASE
	        WHEN ABS(cost_variance_pct) <= 2 THEN 'Stable'
	        WHEN ABS(cost_variance_pct) <= 5 THEN 'Slightly Variable'
	        WHEN ABS(cost_variance_pct) <= 10 THEN 'Variable'
	        ELSE 'Highly Variable'
	      END,
	
	    'lead_time_band',
	      CASE
	        WHEN avg_lead_time_days <= 14 THEN 'Fast'
	        WHEN avg_lead_time_days <= 30 THEN 'Moderate'
	        WHEN avg_lead_time_days <= 60 THEN 'Slow'
	        ELSE 'Very Slow'
	      END,
	
	    'defect_band',
	      CASE
	        WHEN defect_rate_pct <= 1 THEN 'Excellent'
	        WHEN defect_rate_pct <= 3 THEN 'Good'
	        WHEN defect_rate_pct <= 5 THEN 'Moderate'
	        ELSE 'High'
	      END,
	
	    'compliance_band',
	      CASE
	        WHEN compliance_score >= 95 THEN 'Excellent'
	        WHEN compliance_score >= 85 THEN 'Strong'
	        WHEN compliance_score >= 70 THEN 'Adequate'
	        ELSE 'Weak'
	      END,
	
	    'risk_band',
	      CASE
	        WHEN risk_score >= 80 THEN 'High'
	        WHEN risk_score >= 60 THEN 'Medium'
	        WHEN risk_score >= 40 THEN 'Low'
	        ELSE 'Very Low'
	      END,
	
	    'breach_risk_band',
	      CASE
	        WHEN contract_breach_count >= 3 THEN 'High'
	        WHEN contract_breach_count >= 1 THEN 'Medium'
	        ELSE 'Low'
	      END,
	
	    'performance_band',
	      CASE
	        WHEN supplier_performance_score >= 85 THEN 'Excellent'
	        WHEN supplier_performance_score >= 70 THEN 'Good'
	        WHEN supplier_performance_score >= 55 THEN 'Average'
	        ELSE 'Poor'
	      END 
		) as metadata
		-- metadata
from supplier_data
);

-- truncate table supplier;
select * from supplier;

-- get count
select count(1) from supplier_data;
select count(1) from supplier;

select * from supplier_data;
select * from supplier;

