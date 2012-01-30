/* convert auth_user to InnoDB */
/* convert auth_userprofile to InnoDB and add indices */
/* convert django_site to InnoDB */
/* convert multishop_multishopproduct to InnoDB */
/* convert multishop_multishopproduct_virtual_sites to InnoDB and add indices */
/* convert skins_skin to InnoDB and add indices */

ALTER TABLE `hochzeitspedia`.`area_taxrate` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_contact` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_contactinteractiontype` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_contactorganization` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_contactorganizationrole` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_contactrole` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_interaction` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`contact_organization` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`product_attributeoption` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`product_option` ADD COLUMN `site_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`product_taxclass` ADD COLUMN `site_id` int(11) DEFAULT NULL;