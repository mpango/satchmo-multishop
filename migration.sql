/* convert auth_user to InnoDB */
/* convert auth_userprofile to InnoDB and add indices */
/* convert django_site to InnoDB */
/* convert multishop_multishopproduct to InnoDB */
/* convert multishop_multishopproduct_virtual_sites to InnoDB and add indices */
/* convert skins_skin to InnoDB and add indices */

# Adding a site attribute to relevant models.
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

# Stores whether a site represents a multishop (is_multishop = 1) or a normal shop (is_multishop = 0).
ALTER TABLE `hochzeitspedia`.`django_site` ADD COLUMN `is_multishop` tinyint(1) NOT NULL DEFAULT '0';

# Adds a reference from normal orders to their parent multishoporder (if present).
ALTER TABLE `hochzeitspedia`.`shop_order` ADD COLUMN `multishop_order_id` int(11) DEFAULT NULL;
ALTER TABLE `hochzeitspedia`.`shop_order` ADD CONSTRAINT `multishop_order_id_refs_id_26f5d305` FOREIGN KEY (`multishop_order_id`) REFERENCES `shop_order` (`id`);